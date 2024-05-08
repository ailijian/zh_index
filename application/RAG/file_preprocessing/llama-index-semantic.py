# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/30 14:18
@Author  : minglang.wu
@File    : llama-index-semantic.py
@Desc    :
"""
import re

from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.bridge.pydantic import Field

from application.models.embedding.EmbeddingLlamaIndex import get_embedding_with_llama_index
from application.models.llm.ErnieLlamaIndex import Ernie

# from llama_index_test.libs.extractor.regex_extractor import RegexExtractor

"""
$ pip install llama-index llama-index-core llama-index-embeddings-openai llama-index-embeddings-huggingface
"""

from llama_index.core import SimpleDirectoryReader, Document, VectorStoreIndex, Settings, get_response_synthesizer
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser, MetadataAwareTextSplitter, TextSplitter,
)
from llama_index.core import VectorStoreIndex

# 初始化全局配置
# import llama_index_test.setting

pdf_file = "../data/PDF/关于发布《涉税专业服务基本准则（试行）》和《涉税专业服务职业道德守则（试行）》的公告.pdf"
docs = SimpleDirectoryReader(input_files=[pdf_file]).load_data(show_progress=True)


class RegexSplitter(TextSplitter):
    pattern: str = Field(description="Regex pattern to match.")

    def __init__(self, pattern: str, **kwargs):
        super().__init__(
            pattern=pattern,
            **kwargs
        )

    def split_text(self, text: str):
        s = re.split(self.pattern, text)
        print(s)
        return s


def base_plan_q_engine(documents):
    """
    基础分割
    :param documents:
    :return:
    """
    # splitter = SentenceSplitter(chunk_size=512, chunk_overlap=20, secondary_chunking_regex=r'第\D{1,4}章')
    splitter = RegexSplitter(pattern=r"第\D{1,4}章")
    nodes = splitter.get_nodes_from_documents(documents)
    print("************ base split node ************")
    for n in nodes:
        print("  [DEBUG] text:\n", n.text)
        print("  [DEBUG] metadata:\n", n.metadata)
        print("************ - ************")
    vector_index = VectorStoreIndex(nodes)
    query_engine = vector_index.as_query_engine()
    return query_engine


def semantic_plan_q_engine(documents):
    """
    语义分割 + 正则提取章节->metadata
    :param documents:
    :return:
    """
    transformations = [
        SemanticSplitterNodeParser(buffer_size=5, breakpoint_percentile_threshold=95, embed_model=Settings.embed_model),
        RegexExtractor(pattern=r"第\D{1,4}章"),
    ]
    vector_index = VectorStoreIndex.from_documents(documents, transformations=transformations)
    # query_engine = vector_index.as_query_engine()
    retriever = VectorIndexRetriever(
        index=vector_index,
        similarity_top_k=3,
        verbose=True
    )
    res = retriever.retrieve("涉税专业服务业务实施过程中，如何确保业务成果的质量？（中文回答）")
    for r in res:
        print(r.text, r.score, r.metadata)
    # configure response synthesizer
    response_synthesizer = get_response_synthesizer(response_mode="compact_accumulate")
    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer
    )
    return query_engine


# 设定LLM
Settings.llm = Ernie()

# 设定embedding model
Settings.embed_model = get_embedding_with_llama_index()

# Question
Q_list = [
    "涉税专业服务业务实施过程中，如何确保业务成果的质量？（中文回答）"
]

query_engine_list = [
    base_plan_q_engine(docs),
    # semantic_plan_q_engine(docs),
]

for query_engine in query_engine_list:
    for q in Q_list:
        print("Query: \n  ", q)
        print("Answer: \n  ", query_engine.query(q))
        print("===")

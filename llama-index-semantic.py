# -*- coding: utf-8 -*-
"""
@Time    : 2024/4/30 14:18
@Author  : minglang.wu
@File    : llama-index-semantic.py
@Desc    :
"""

"""
$ pip install llama-index llama-index-core llama-index-embeddings-openai llama-index-embeddings-huggingface
"""

import os
from llama_index.core import SimpleDirectoryReader, Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
os.environ["OPENAI_API_KEY"] = "sk-a3tRIN1OtE4Y0UG2bN09W6vRpfDHcJOJXDQ9rpEavUt72iYf"
os.environ["OPENAI_API_BASE"] = "https://api.chatanywhere.tech/v1"

pdf_file = "application/database/enterprise_info/PDF/关于发布《涉税专业服务基本准则（试行）》和《涉税专业服务职业道德守则（试行）》的公告.pdf"
docs = SimpleDirectoryReader(input_files=[pdf_file]).load_data(show_progress=True)

# embed_model = OpenAIEmbedding()
embed_model = HuggingFaceEmbedding(
    model_name=r"E:\models\bge-base-zh-v1.5",
    # cache_folder=r"E:\models"
)

# 分割器
splitter = SemanticSplitterNodeParser(
    buffer_size=2, breakpoint_percentile_threshold=95, embed_model=embed_model
)
base_splitter = SentenceSplitter(chunk_size=512)

# 分割文档节点
nodes = splitter.get_nodes_from_documents(docs)
print(nodes[1].get_content())
print("==================")

base_nodes = base_splitter.get_nodes_from_documents(docs)

# 生成索引引擎
from llama_index.core import VectorStoreIndex

vector_index = VectorStoreIndex(nodes)
query_engine = vector_index.as_query_engine()

base_vector_index = VectorStoreIndex(base_nodes)
base_query_engine = base_vector_index.as_query_engine()

# 分别query
Q_list = [
    "涉税专业服务业务实施过程中，如何确保业务成果的质量？"
]
response = query_engine.query(
    Q_list[0]
)
print("response:", response)
base_response = base_query_engine.query(
    Q_list[0]
)
print("base_response:", base_response)

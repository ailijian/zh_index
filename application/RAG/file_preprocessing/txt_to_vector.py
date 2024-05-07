from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader, SummaryIndex, Settings
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)

from application.models.embedding.EmbeddingLlamaIndex import get_embedding_with_llama_index
from application.models.llm.ErnieLlamaIndex import Ernie
import llama_index.core
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
loglog = llama_index.core.set_global_handler("simple")


def customer_documents(docs: list):
    """一个手动创建的文档列表，用于构建索引。"""
    # 创建文档
    cus_documents = []
    for doc in docs:
        cus_documents.append(
            Document(
                text=doc["text"],
                metadata={"filename": doc["filename"], "category": doc["category"]},
            )
        )
    for document in cus_documents:
        print("打印document：", document)
        print("打印document.text：", document.text)
        print("打印document.metadata：", document.metadata)
    return cus_documents


def chat_engine():
    """一个搜索方法"""
    from llama_index.core.chat_engine import SimpleChatEngine
    from llama_index.core.prompts.system import IRS_TAX_CHATBOT

    chat_engine = SimpleChatEngine.from_defaults(system_prompt=IRS_TAX_CHATBOT)
    response = chat_engine.chat(
        "Say something profound and romantic about fourth of July"
    )
    print(response)
    return response


def load_documents():
    """一个加载文档的方法"""
    # 加载文档
    directory_path = r"./data/pdf"
    documents = SimpleDirectoryReader(
        input_dir=directory_path,
        recursive=True,  # recursive=True是开启读取子目录
        # required_exts=[".pdf", ".docx"],  # 只读取指定扩展名的文件
        # num_files_limit=100,  # 限制读取的文件数量
    ).load_data()
    return documents


def node_parser(documents):
    """一个基础节点解析器函数"""
    # 按语义分割成节点
    parser = SentenceSplitter(
        separator="\n",
        chunk_size=1024,
        chunk_overlap=20,
    )
    nodes = parser.get_nodes_from_documents(documents)
    print("打印nodes的块：", nodes[1].get_content())
    print("打印node_parser_nodes：", nodes)
    return nodes


def semantic_splitter(documents, embed_model):
    """一个将文档按语义分割的函数"""
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    nodes = splitter.get_nodes_from_documents(documents)
    print("打印semantic_splitter_nodes：", nodes)
    return nodes


def customer_node():
    """一个自定义节点的函数"""
    from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo

    node1 = TextNode(text="<text_chunk>", id_="<node_id>")
    node2 = TextNode(text="<text_chunk>", id_="<node_id>")
    # set relationships
    node1.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
        node_id=node2.node_id
    )
    node2.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
        node_id=node1.node_id, metadata={"key": "val"}
    )
    nodes = [node1, node2]
    return nodes


def metadata_extractor(documents):
    """一个提取元数据并制作成节点的函数"""
    from llama_index.core.extractors import (
        KeywordExtractor,
        PydanticProgramExtractor,
        QuestionsAnsweredExtractor,
        SummaryExtractor,
        TitleExtractor,
    )
    from llama_index.core.node_parser import TokenTextSplitter

    text_splitter = TokenTextSplitter(
        separator="\n", chunk_size=512, chunk_overlap=51
    )
    print("打印text_splitter：", text_splitter)
    title_extractor = TitleExtractor(nodes=5)
    print("打印title_extractor：", title_extractor)
    qa_extractor = QuestionsAnsweredExtractor(questions=3)
    print("打印qa_extractor：", qa_extractor)

    # assume documents are defined -> extract nodes
    from llama_index.core.ingestion import IngestionPipeline

    pipeline = IngestionPipeline(
        transformations=[text_splitter, title_extractor, qa_extractor]
    )

    nodes = pipeline.run(
        documents=documents,
        in_place=True,
        show_progress=True,
    )
    print("打印nodes：", nodes)
    return nodes


def file_node_parsers(file_path):
    """一个根据文件类型，自动选择最佳处理方式的函数"""
    from llama_index.core.node_parser import SimpleFileNodeParser
    from llama_index.readers.file import FlatReader
    from pathlib import Path

    reader = FlatReader()
    html_file = reader.load_data(Path("./stack-overflow.html"))
    md_file = reader.load_data(Path("./README.md"))
    print(html_file[0].metadata)
    print(html_file[0])
    print("----")
    print(md_file[0].metadata)
    print(md_file[0])

    parser = SimpleFileNodeParser()
    md_nodes = parser.get_nodes_from_documents(md_file)
    html_nodes = parser.get_nodes_from_documents(html_file)
    print(md_nodes[0].metadata)
    print(md_nodes[0].text)
    print(md_nodes[1].metadata)
    print(md_nodes[1].text)
    print("----")
    print(html_nodes[0].metadata)
    print(html_nodes[0].text)

    return md_nodes,  html_nodes

def wind_index(documents, llm, embed_model):
    """一个用上下文窗口替换召回文本段的函数"""
    from llama_index.core.node_parser import SentenceWindowNodeParser
    from llama_index.core.node_parser import SentenceSplitter

    # create the sentence window node parser w/ default settings
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )

    # base node parser is a sentence splitter
    text_splitter = SentenceSplitter()


    from llama_index.core import Settings
    # 将llm，embedding，切个好的文本设置到Settings中
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.text_splitter = text_splitter

    # 定义窗口node和普通node
    nodes = node_parser.get_nodes_from_documents(documents)
    base_nodes = text_splitter.get_nodes_from_documents(documents)

    from llama_index.core import VectorStoreIndex
    # 创建窗口索引和普通索引
    sentence_index = VectorStoreIndex(nodes)
    base_index = VectorStoreIndex(base_nodes)

    from llama_index.core.postprocessor import MetadataReplacementPostProcessor
    # 用上下文窗口替换召回文本段的结果
    query_engine = sentence_index.as_query_engine(
        similarity_top_k=2,
        # the target key defaults to `window` to match the node_parser's default
        node_postprocessors=[
            MetadataReplacementPostProcessor(target_metadata_key="window")
        ],
    )
    window_response = query_engine.query(
        "What are the concerns surrounding the AMOC?"
    )
    print(window_response)

    window = window_response.source_nodes[0].node.metadata["window"]
    sentence = window_response.source_nodes[0].node.metadata["original_text"]

    print(f"Window: {window}")
    print("------------------")
    print(f"Original Sentence: {sentence}")

    # 分析每个召回的块
    for source_node in window_response.source_nodes:
        print(source_node.node.metadata["original_text"])
        print("--------")

    # 普通检索召回结果
    query_engine = base_index.as_query_engine(similarity_top_k=2)
    vector_response = query_engine.query(
        "What are the concerns surrounding the AMOC?"
    )
    print(vector_response)

    # 分析普通检索召回的块
    for node in vector_response.source_nodes:
        print("AMOC mentioned?", "AMOC" in node.node.text)
        print("--------")
    print(vector_response.source_nodes[2].node.text)
    print("--------")

# def evaluation():
    """一个对RAG结果进行评估的函数"""
    from llama_index.core.evaluation import DatasetGenerator, QueryResponseDataset

    from llama_index.llms.openai import OpenAI
    import nest_asyncio
    import random

    nest_asyncio.apply()
    len(base_nodes)
    num_nodes_eval = 30
    # there are 428 nodes total. Take the first 200 to generate questions (the back half of the doc is all references)
    sample_eval_nodes = random.sample(base_nodes[:200], num_nodes_eval)
    # NOTE: run this if the dataset isn't already saved
    # generate questions from the largest chunks (1024)
    dataset_generator = DatasetGenerator(
        sample_eval_nodes,
        llm=OpenAI(model="gpt-4"),
        show_progress=True,
        num_questions_per_chunk=2,
    )

    eval_dataset = await dataset_generator.agenerate_dataset_from_nodes()

    eval_dataset.save_json("data/ipcc_eval_qr_dataset.json")

    # optional
    eval_dataset = QueryResponseDataset.from_json("data/ipcc_eval_qr_dataset.json")

    import asyncio
    import nest_asyncio

    nest_asyncio.apply()

    from llama_index.core.evaluation import (
        CorrectnessEvaluator,
        SemanticSimilarityEvaluator,
        RelevancyEvaluator,
        FaithfulnessEvaluator,
        PairwiseComparisonEvaluator,
    )

    from collections import defaultdict
    import pandas as pd

    # NOTE: can uncomment other evaluators
    evaluator_c = CorrectnessEvaluator(llm=OpenAI(model="gpt-4"))
    evaluator_s = SemanticSimilarityEvaluator()
    evaluator_r = RelevancyEvaluator(llm=OpenAI(model="gpt-4"))
    evaluator_f = FaithfulnessEvaluator(llm=OpenAI(model="gpt-4"))
    # pairwise_evaluator = PairwiseComparisonEvaluator(llm=OpenAI(model="gpt-4"))

    from llama_index.core.evaluation.eval_utils import (
        get_responses,
        get_results_df,
    )
    from llama_index.core.evaluation import BatchEvalRunner

    max_samples = 30

    eval_qs = eval_dataset.questions
    ref_response_strs = [r for (_, r) in eval_dataset.qr_pairs]

    # resetup base query engine and sentence window query engine
    # base query engine
    base_query_engine = base_index.as_query_engine(similarity_top_k=2)
    # sentence window query engine
    query_engine = sentence_index.as_query_engine(
        similarity_top_k=2,
        # the target key defaults to `window` to match the node_parser's default
        node_postprocessors=[
            MetadataReplacementPostProcessor(target_metadata_key="window")
        ],
    )

    import numpy as np

    base_pred_responses = get_responses(
        eval_qs[:max_samples], base_query_engine, show_progress=True
    )
    pred_responses = get_responses(
        eval_qs[:max_samples], query_engine, show_progress=True
    )

    pred_response_strs = [str(p) for p in pred_responses]
    base_pred_response_strs = [str(p) for p in base_pred_responses]

    evaluator_dict = {
        "correctness": evaluator_c,
        "faithfulness": evaluator_f,
        "relevancy": evaluator_r,
        "semantic_similarity": evaluator_s,
    }
    batch_runner = BatchEvalRunner(evaluator_dict, workers=2, show_progress=True)

    eval_results = await batch_runner.aevaluate_responses(
        queries=eval_qs[:max_samples],
        responses=pred_responses[:max_samples],
        reference=ref_response_strs[:max_samples],
    )

    base_eval_results = await batch_runner.aevaluate_responses(
        queries=eval_qs[:max_samples],
        responses=base_pred_responses[:max_samples],
        reference=ref_response_strs[:max_samples],
    )

    results_df = get_results_df(
        [eval_results, base_eval_results],
        ["Sentence Window Retriever", "Base Retriever"],
        ["correctness", "relevancy", "faithfulness", "semantic_similarity"],
    )
    display(results_df)


if __name__ == '__main__':
    # 设定LLM
    Settings.llm = Ernie()

    # 设定embedding model
    Settings.embed_model = get_embedding_with_llama_index()

    # 获取文档
    documents = load_documents()
    # 制作节点
    nodes = node_parser(documents)
    # 提取元数据
    # metadata = metadata_extractor(documents)
    # 创建索引
    index = VectorStoreIndex(nodes)

    # 输入查询语句获得回答
    query_engine = index.as_query_engine()
    answer = query_engine.query("涉税专业服务基本准则（试行）的发布日期是什么时候？")
    print("答案：", answer)

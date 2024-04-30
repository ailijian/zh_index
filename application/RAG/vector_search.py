#  定义向量查询
import os
import numpy as np
import time
from application.RAG import vector_store
from application.RAG.file_preprocessing import doc_to_vector
from application.models.embedding import embeddings


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 的运行时间 {end_time - start_time} ")
        return result

    return wrapper


#  封装一个用于文心agent的向量查询类，这里选用的是faiss向量数据库，也可以用milvus等其他向量数据库
class FaissSearch:
    def __init__(self, db, embeddings):
        # 类的初始化方法，接收一个数据库实例并将其存储在类的实例变量 self.db 中，接收一个embeddings方法传到self.embeddings中
        self.db = db
        self.embeddings = embeddings

    @timer_decorator
    def search(self, query: str, top_k: int = 5, **kwargs):
        """一个输入query和想要召回的文本段数量top_k（默认召回10条），获得检索结果的函数"""
        # 调用faiss数据库的 similarity_search_with_score 方法来获取与查询最相关的文档
        docs_and_scores = self.db.similarity_search_with_score(query, top_k)
        # 遍历每个文档，将内容、相似度得分和来源标题作为字典添加到结果列表中
        # retrieval_results = []
        # for i in range(len(docs_and_scores)):
        #     retrieval_results.append(
        #         {
        #             'content': docs_and_scores[i][0].page_content,
        #             'metadata': docs_and_scores[i][0].metadata,
        #             "score": docs_and_scores[i][1],
        #         }
        #     )
        retrieval_results = [{'content': doc.page_content, 'metadata': doc.metadata, 'score': score} for doc, score
                             in docs_and_scores]
        return retrieval_results


# 用langchain创建一个RAG检索方法
def retrieval_results(query, top_k, db, embedding_model):
    """一个传入query和召回文本段数量（默认召回10段），获取检索结果的函数"""
    # metadata = doc_to_vector.get_excel_docs()
    # split_docs = doc_to_vector.list_to_document(metadata)
    # 定义embedding模型
    # embedding_model = embeddings.get_embedding_with_langchain()
    #  创建一个Faiss实例，使用split_docs和embedding_model
    # db = vector_store.get_faiss_db(split_docs)

    # 将FaissSearch实例和embedding模型传入FunctionAgentWithRetrieval
    faiss_search = FaissSearch(db=db, embeddings=embedding_model)
    return faiss_search.search(query, top_k=top_k)

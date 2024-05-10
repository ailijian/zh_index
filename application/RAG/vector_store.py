#  定义向量储存
import os
from langchain_community.vectorstores import FAISS


# 将处理好的Document文档向量化
class VectorStore:
    def get_faiss_db(split_docs, faiss_name="faiss_1", embedding_model=None):
        """一个传入切割好的文档以及embedding模型，存入faiss数据库，返回索引的函数"""
        if os.path.exists(faiss_name):
            # db = FAISS.load_local(faiss_name, embedding_model, allow_dangerous_deserialization=True)
            db = FAISS.load_local(faiss_name, embedding_model)
            return db
        else:
            db = FAISS.from_documents(split_docs, embedding_model)  # 存入faiss数据库
            db.save_local(faiss_name)  # 建立faiss索引，避免重复创建数据库
            return db

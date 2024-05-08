#  定义各类embedding以及对应的方法
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from application.config import setting


# 定义langchain所用的embedding模型
def get_embedding_with_langchain():
    """一个定义langchain所用的embedding模型的函数"""

    model_name = setting.embedding_model_path
    model_kwargs = {"device": "cuda"}
    encode_kwargs = {"normalize_embeddings": True}  # 设置为True就是计算余弦相似度
    embedding_model = HuggingFaceBgeEmbeddings(
        model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs,
        query_instruction="为这个句子生成表示以用于检索相关文章："
    )
    return embedding_model

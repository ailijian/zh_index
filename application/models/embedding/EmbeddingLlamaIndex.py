#  定义各类embedding以及对应的方法
from application.config import setting
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# 定义llama-index所用的embedding模型
def get_embedding_with_llama_index():
    """一个定义langchain所用的embedding模型的函数"""
    embedding_model = HuggingFaceEmbedding(
        model_name=setting.embedding_model_path,
        device="cuda",
        # normalize=True,  # 设置为True就是计算余弦相似度
        query_instruction="为这个句子生成表示以用于检索相关文章："
    )
    return embedding_model

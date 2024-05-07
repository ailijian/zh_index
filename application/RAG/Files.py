# 对各种格式的文件预处理，包括加载、抽取元数据、储存、索引和嵌入
from llama_index.core import Document, SimpleDirectoryReader, Settings

from application.models.embedding.EmbeddingLlamaIndex import get_embedding_with_llama_index
from application.models.llm.ErnieLlamaIndex import Ernie


class Files:
    def __init__(self):
        pass

    @staticmethod
    def load_simple_files(directory):
        """
        一个加载简单常见的文件并组装为document格式的函数，包括：
        txt
        word
        pdf
        ppt
        """
        documents = SimpleDirectoryReader(
            input_dir=directory,
            # recursive=True,  # recursive=True是开启读取子目录
            # required_exts=[".pdf", ".docx"],  # 只读取指定扩展名的文件
            # num_files_limit=100,  # 限制读取的文件数量
        ).load_data()
        return documents

    @staticmethod
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


if __name__ == '__main__':
    # 设定LLM
    Settings.llm = Ernie()

    # 设定embedding model
    Settings.embed_model = get_embedding_with_llama_index()

    # 演示
    file_directory = "./data/pdf"
    docs = Files.load_simple_files(file_directory)


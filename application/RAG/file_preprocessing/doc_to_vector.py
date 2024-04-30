from FlagEmbedding import FlagModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

from extend.mysql.sql import Sql
import mysql.connector
from config import setting


def split_documents(documents, size=500, overlap=50):
    """一个对输入文本文档按设定进行切分的函数"""
    set_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap,
                                                  separators=["\n\n", "\n", "。", "，", " "])
    split_docs = set_splitter.split_documents(documents)
    return split_docs


# split_docs = split_documents(pdf_docs,384)
# print(split_docs)

#  读取Excel文件里的所有字段信息
def get_excel_docs(types=1):
    #  mysql 获取：
    result = []
    if types == 1:
        # 切割文本
        data_sql = select_qa_pair('ai_vector_library')
        for key in data_sql:
            result.append(
                {
                    'id': key['id'],
                    'name': key['name'],
                    'text': key['text'],
                    'page': key['page'],
                    'file': key['file'],
                    'answer': '',
                }
            )
    else:
        # 问答对
        data_sql = select_qa_pair('ai_vector_library_wendadui')
        for key in data_sql:
            result.append(
                {
                    'id': key['id'],
                    'name': key['name'],
                    'text': key['text'],
                    'page': key['page'],
                    'file': key['file'],
                    'answer': key['answer'],
                }
            )


        # 注意=====》 问答对（读取表：ai_vector_library_wendadui）情况下：answer就是答案，text：就是问题
    return result


#  查询数据库
def select_qa_pair(table):
    sql = "SELECT * FROM " + table
    cnx = mysql.connector.connect(user=setting.user, password=setting.password, host=setting.host,
                                  database=setting.database)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    if result:
        return result
    return []


# 遍历读取的excel数据，将数据重组为Document_list
def metadata_to_document(metadata):
    """一个遍历读取的excel数据，将数据重组为Document_list的函数"""
    Document_list = []
    for entry in metadata:
        paragraph_title = entry["text"]
        metadata = entry
        Document_list.append([paragraph_title, metadata])
    return Document_list


# 一个Document类，用于存储页面内容和元数据
class Document:
    """一个Document类，用于存储页面内容和元数据"""

    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"Document(page_content='{self.page_content}', metadata={self.metadata})"


# 调用Document类，将数据重组为langchain接受的，用来存入faiss数据库的Document数据
def list_to_document(metadata):
    """一个将数据重组为langchain接受的，用来存入faiss数据库的Document数据的函数"""
    Document_list = metadata_to_document(metadata)
    documents = []
    for document in Document_list:
        # print(document)
        document_ = Document(page_content=document[0], metadata=document[1])
        # 创建Document实例
        documents.append(document_)
    # print(documents[:100])
    return documents

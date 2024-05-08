# 对各种格式的文件预处理，包括加载、抽取元数据、储存、索引和嵌入
from llama_index.core import Document, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from application.models.embedding.EmbeddingLlamaIndex import get_embedding_with_llama_index
from application.models.llm.ErnieLlamaIndex import Ernie
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader, PyPDFDirectoryLoader


class Files:
    def __init__(self):
        pass

    @staticmethod
    def merge_texts(cut_texts):
        while len(cut_texts) > 1:
            merged_text = cut_texts[-1]
            tokens = merged_text.split()
            if len(tokens) > 200:
                return merged_text  # 返回token数量大于200的文本
            else:
                # 移除可能存在的多余空格和结尾的标点符号
                merged_text = merged_text.rstrip('.!?，。！？')
                prev_text = cut_texts[-2].rstrip('.!?，。！？')
                cut_texts[-2] = prev_text + '。' + merged_text
                cut_texts.pop()  # 移除已合并的最后一个文本
        # 如果所有文本都已合并，则返回合并后的单个文本
        return cut_texts[0]

    @staticmethod
    def cut_text_by_rules(text, size=120):
        cut_texts = []  # 存储最终切割好的文本段

        # 第一步：先以“\n”为分隔符进行切割
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            paragraph = paragraph.strip()  # 去除首尾的空白字符
            if not paragraph:
                continue  # 跳过空段落

            # 第二步：再按“。”进行切割
            sentences = paragraph.split('。')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:  # 跳过空句子
                    cut_texts.append(sentence + '。')  # 添加句子，并补回句号

        print("初步分割cut_texts：", cut_texts)

        cut_texts = Files.merge_texts(cut_texts)

        print("最终cut_texts：", cut_texts)

        return cut_texts

    @staticmethod
    def load_simple_files(directory, page_overlap: int = 120):
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
        print("打印documents文档：\n", documents)
        # 打印看看
        for document in documents:
            document.text = document.text
            print("document>>>>>>>", document.get_content())

        # 默认的方法是按页面切割的，页面之间没有内容重叠，导致后面做节点处理的时候，即使设置了overlap，也会有页面之间的内容缺失
        # 所以在此处，我们自定一个实现页面之间overlap的方法

        # 遍历docs列表，从第二个元素开始修改text值
        for i in range(1, len(documents)):
            if i > 0:
                previous_text = documents[i - 1].text

                # 按要求获取上一页的overlap
                cut_previous_text = Files.cut_text_by_rules(previous_text, page_overlap)

                current_text = documents[i].text
                # 取前一个元素的text值的后overlap_length个字符，并与当前元素的text值拼接
                overlap_text = ''.join(cut_previous_text) + current_text
                documents[i].text = overlap_text

        # 打印看看重叠部分加上没
        for document in documents:
            document.text = document.text
            # print("document[0]>>>>>>>", document.text)
            print("overlap_document>>>>>>>", document.get_content())
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

    @staticmethod
    def node_parser(documents):
        """一个基础节点解析器函数"""
        # 按语义分割成节点
        parser = SentenceSplitter(
            separator="\n",
            chunk_size=1024,
            chunk_overlap=240,
        )
        nodes = parser.get_nodes_from_documents(documents)
        # print("打印nodes的块：", nodes[1].get_content())
        # print("打印node_parser_nodes：\n", nodes)
        return nodes

    @staticmethod
    def semantic_splitter(documents, embed_model):
        """一个将文档按语义分割的函数"""
        splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
        )
        nodes = splitter.get_nodes_from_documents(documents)
        print("打印semantic_splitter_nodes：", nodes)
        return nodes

    @staticmethod
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


if __name__ == '__main__':
    # 设定LLM
    Settings.llm = Ernie()

    # 设定embedding model
    Settings.embed_model = get_embedding_with_llama_index()

    # 获取文档
    file_directory = "./data/pdf"
    documents = Files.load_simple_files(file_directory)
    # print("打印documents文档：\n", documents)
    # print("############################")
    # for document in documents:
    #     print("打印document文档：\n", document)
    #     print("############################")

    # # 打印直接加载的文档
    # pdf_docs = Files.load_pdf_documents("./data/PDF")
    # print("打印直接加载的文档：\n", pdf_docs)
    # print("############################")
    # for pdf_doc in pdf_docs:
    #     print("打印直接加载的文档：\n", pdf_doc)
    #     print("############################")
    #
    # # 打印直接加载的文档
    # split_docs = Files.split_documents(pdf_docs)
    # print("打印langchain切割的文档：\n", split_docs)
    # print("############################")
    # for split_doc in split_docs:
    #     print("打印langchain切割的文档：\n", split_doc)
    #     print("############################")

    # 制作节点
    nodes = Files.node_parser(documents)
    print("打印llama index的nodes：\n", nodes)
    print("############################")
    for node in nodes:
        print("打印node_id：\n", node.node_id)
        print("打印node_metadata：\n", node.metadata)
        print("打印node_content：\n", node.get_content())
        print("############################")

    # 测试语义分割
    # semantic_nodes = Files.semantic_splitter(documents, embed_model=get_embedding_with_llama_index())
    # for semantic_node in semantic_nodes:
    #     print("打印semantic_node节点：\n", semantic_node)
    #     print("############################")

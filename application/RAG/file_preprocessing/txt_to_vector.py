from llama_index.core import Document

doc = Document(text="text")
document = Document(
    text="text",
    metadata={"filename": "<doc_file_name>", "category": "<category>"},
)
print("打印doc：", doc)
print("打印doc.text：", doc.text)
print("打印document.metadata：", document.metadata)
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import llama_index.core

loglog = llama_index.core.set_global_handler("simple")
print("回调信息：", loglog)

# from llama_index.core import VectorStoreIndex
#
# # from_documents还需要一个可选参数show_progress。将其设置为True在索引构建期间显示进度条。
# index = VectorStoreIndex.from_documents(documents=document, show_progress=True)

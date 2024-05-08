# [mysql]
# 数据库
user = "rose_test"
password = "AnM7sWk8Wkx75Mis"
host = "47.100.0.189"
database = "rose_test"
des = "线上数据库"

# user = "root"
# password = "123456"
# host = "localhost"
# database = "robots"
# des = "本地数据库"



# [Token]
#  设置文心一言的token
# ERNIEBOT_ACCESS_TOKEN = "305b5ef9b5fcc3d1fca148fa80b31c306fc06415"  # 杨涛的token
ERNIEBOT_ACCESS_TOKEN = "305b5ef9b5fcc3d1fca148fa80b31c306fc06415"  # 李健的token

#  设置百川的api_key
BAICHUAN_API_KEY = "sk-0afe222def5e2b5e8b8bf81671c3286f"

# OCR_KEY
API_KEY = "5elO3CilAMuozBoFOxG3uPa0"
SECRET_KEY = "4j5IUiAuM3xTyCF1U6e8ovDzpnxFpxbL"

# 使用阿里的KEY
DASHSCOPE_API_KEY = "sk-c5c2c9e8ed5940e7a92122ae4824db47"

# [Embedding]
embedding_model_path = r"E:\models\bge-base-zh-v1.5"  # 李健公司电脑本地
path = "./model_file/bge-base-zh-v1.5"  # 服务器
# path = r"E:\models\bge-base-zh-v1.5"  # 李健本地
reranker_path = "./model_file/bge-reranker-base"

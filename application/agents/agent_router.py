# 封装一个agent路由方法
import asyncio
import json
import time

from application.RAG.vector_search import retrieval_results
from application.agents.chat_agent import ChatAgent
from application.agents.intention_agent import IntentionAgent
from application.agents.retrieval_agent import RetrieveAgent
from common.common import Common
from application.RAG import vector_store
from application.RAG.file_preprocessing import doc_to_vector
from application.models.embedding import Embedding
from application.database.user_info.messages import get_user_message

# 实例化意图agent
intention_agent = IntentionAgent()
# 实例化检索agent
retrieve_agent = RetrieveAgent()
# 实例化聊天agent
chat_agent = ChatAgent()


async def update_ui(result_file: list, emit=None, socketid=None):
    # 遍历所有文件
    seen_file_names = set()
    unique_files = []
    for file in result_file:
        file_name = file['file_name']
        # 如果file_name不在集合中，则添加到集合和结果列表中
        if file_name not in seen_file_names:
            seen_file_names.add(file_name)
            unique_files.append(file)
    data = {
        'code': 200,
        'sikao': 1,
        'file': unique_files,
    }
    Common().log_ini_add('文件分析打印', '222222', str(data))
    """一个将检索信息同步到前端页面的函数"""
    emit(str(socketid), data)


# async def extract_json_from_llm_answer(result, start_str="```json", end_str="```", replace_list=None):
#     """一个将文心大模型返回的json结果解析为标准json格式的函数"""
#     if replace_list is None:
#         replace_list = ["\n"]
#     s_id = result.index(start_str)
#     e_id = result.index(end_str, s_id + len(start_str))
#     json_str = result[s_id + len(start_str):e_id]
#     for replace_str in replace_list:
#         json_str = json_str.replace(replace_str, "")
#     json_dict = json.loads(json_str)
#     return json_dict

async def extract_llm_answer_to_json(result, start_str="```json", end_str="```", replace_list=None):
    """一个从大型语言模型（如GPT等）的回答中提取出JSON格式的数据，并将其解析为Python字典的函数"""
    if replace_list is None:
        replace_list = ["\n"]

    try:
        s_id = result.index(start_str)
        e_id = result.index(end_str, s_id + len(start_str))
        json_str = result[s_id + len(start_str):e_id]

        for replace_str in replace_list:
            json_str = json_str.replace(replace_str, "")

        json_dict = json.loads(json_str)
        return json_dict

    except json.JSONDecodeError as e:
        # 如果 JSON 解析失败，则返回 None
        print("JSON Decode Error:", e)
        return None

    except ValueError as e:
        # 如果找不到起始字符串或结束字符串，则返回 None
        print("Error:", e)
        return None


async def retrieval_filter(retrieval_results: list, threshold: float = 1.03):
    """一个传入检索结果，按要求过滤后返回想要的检索结果的函数"""
    result_text = ""  # 纯文本检索结果
    result_file = []  # 示例[{"file_name":"文件名1", "file_path":"文件路径1", "page":"页码1"},{"file_name":"文件名2", "file_path":"文件路径2", "page":"页码2"}]
    for item in retrieval_results:
        score = item['score']
        if score < threshold:
            result_text += item['content'] + "\n"
            result_file.append(
                {"file_name": item['metadata']['name'], "file_path": item['metadata']['file'],
                 "page": item['metadata']['page']})
    return {"result_text": result_text, "result_file": result_file}


async def router_chat(user_input: str, chat_history_list: str, user_intention: dict, agent_id: str):
    """闲聊回复函数"""
    result = await chat_agent.chat(user_input=user_input, chat_history=chat_history_list, agent_id=agent_id)
    if isinstance(result, str):
        result = await extract_llm_answer_to_json(result)
    if isinstance(result, dict):
        # 返回的答案为字典格式，包含“意图识别结果、回答结果、检索结果”，其中闲聊不需要检索知识库，所以检索结果为空
        return {"intention": user_intention["intention"],
                "answer": [result["response"]["answer"] + result["response"]["relative"]], "retrieve_results": "",
                "is_know": "", "is_ok_list": ""}

    else:
        print("\n\n本次回答结果不符合预期的格式...请检查agent_router文件\n\n")


async def router_qa(user_input: str, chat_history_list: str, user_intention: dict, agent_id: str, faiss_db,
                    embedding_model, emit=None,
                    socketid=None):
    """问答回复函数"""
    start_time = time.time()  # 获取初始时间
    # 关键问题检索
    rag_results = retrieval_results(query=user_input + user_intention["topic"], top_k=4, db=faiss_db,
                                    embedding_model=embedding_model)

    end_time1 = time.time()  # 获取检索结束时间
    execution_time1 = end_time1 - start_time  # 计算运行时间
    print(f"\n\n问题检索时间为：{execution_time1}秒\n\n")

    print(f"\n\n打印完整检索内容：{rag_results}\n\n")
    # 过滤掉欧氏距离大于threshold的检索结果，并将其拼接成接下来需要使用的纯文本、文件名和文件路径
    filter_result = await retrieval_filter(retrieval_results=rag_results, threshold=1.03)

    # Common().log_ini_add('文件分析打印', '1', str(data))
    end_time2 = time.time()  # 获取检索答案过滤结束时间
    execution_time2 = end_time2 - end_time1  # 计算运行时间
    print(f"\n\n检索答案过滤时间为：{execution_time2}秒\n\n")

    # 将检索信息传到前端 2024年4月26日20:49:12====》前端未实现对接
    await update_ui(filter_result["result_file"], emit, socketid)
    # 将用户输入内容，历史对话和检索信息传入检索agent，获得回复
    results = await retrieve_agent.retrieve(user_input=user_input, chat_history=chat_history_list,
                                            intention_topic=user_intention["topic"],
                                            retrieve_results=filter_result["result_text"],
                                            agent_id=agent_id)
    if isinstance(results, str):
        results = await extract_llm_answer_to_json(results)
    if isinstance(results, dict):
        is_ok_list = []
        is_know_list = []
        result_list = []
        for r in results["response"]:
            result_list.append(r["initial"] + r["answer"] + r["relative"])
            is_ok_list.append(r["is_ok"])
            is_know_list.append(r["is_know"])
        # result_list = [r["is_know"] + r["initial"] + r["answer"] + r["relative"] for r in results["response"]]
        # 返回的答案为字典格式，包含“意图识别结果、回答结果、检索结果”

        return {"intention": user_intention["intention"], "answer": result_list, "retrieve_results": filter_result,
                "is_know": is_know_list, "is_ok_list": is_ok_list}

    else:
        print("\n\n本次回答结果不符合预期的格式...请检查agent_router文件\n\n")


async def agent_router(user_input, chat_history_list, agent_id: str, faiss_db=None, embedding_model=None, emit=None,
                       socketid=None):
    """一个传入user_input，选择最适合的agent的函数"""
    start_time = time.time()  # 获取初始时间

    # 意图识别：传入当前用户输入内容与历史对话记录
    user_intention = await intention_agent.get_intention(user_input=user_input,
                                                         chat_history_str=chat_history_list["chat_history_str"],
                                                         agent_id=agent_id)

    end_time2 = time.time()  # 获取意图识别结束时间
    execution_time2 = end_time2 - start_time  # 计算运行时间
    print(f"\n\n意图识别的时间为：{execution_time2}秒\n\n")

    if isinstance(user_intention, str):
        user_intention = await extract_llm_answer_to_json(user_intention)
    if isinstance(user_intention, dict):
        print("意图识别结果：", user_intention["intention"])
        # 根据识别结果选择对应的agent
        if user_intention["intention"] == "闲聊":
            chat_result = await router_chat(user_input=user_input, chat_history_list=chat_history_list["chat_history"],
                                            user_intention=user_intention, agent_id=agent_id)

            end_time3 = time.time()  # 获取闲聊执行结束时间
            execution_time3 = end_time3 - end_time2  # 计算运行时间
            print(f"\n\n本轮闲聊agent的回复时间为：{execution_time3}秒\n\n")

            return chat_result
        elif user_intention["intention"] == "咨询":
            qa_result = await router_qa(user_input=user_input, chat_history_list=chat_history_list["chat_history"],
                                        user_intention=user_intention, agent_id=agent_id, faiss_db=faiss_db,
                                        embedding_model=embedding_model, emit=emit, socketid=socketid)

            end_time4 = time.time()  # 获取问答执行结束时间
            execution_time4 = end_time4 - end_time2  # 计算运行时间
            print(f"\n\n本轮问答agent的执行时间为：{execution_time4}秒\n\n")

            return qa_result
        else:
            print("出错啦！！！！！！！！！！没有获得预期的意图，请检查agent_router文件")
    else:
        print("出错啦！！！！！！！！！！意图识别结果不符合预期的格式，请检查agent_router文件")


if __name__ == "__main__":
    embedding_model = embeddings.get_embedding_with_langchain()
    metadata = doc_to_vector.get_excel_docs()
    split_docs = doc_to_vector.list_to_document(metadata)
    db = vector_store.VectorStore.get_faiss_db(split_docs=split_docs, embedding_model=embedding_model)
    while True:
        # chat_history = ""
        # chat_history_list = ["你好", "你好，有什么可以帮你？"]
        # chat_history = "客户：你好\n你：你好，有什么可以帮你？\n"
        user_input = input("请输入测试内容：")
        if user_input == "exit":
            break
        start_time = time.time()  # 获取开始时间
        # 获取用户历史对话记录，这是一个字典，里面有字符串格式的chat_history_str，有大模型标准格式的chat_history
        chat_history_list = get_user_message(user_handle="ihgPoc10000")
        # 回答
        result = asyncio.run(agent_router(user_input=user_input, chat_history_list=chat_history_list,
                                          faiss_db=db, agent_id="test", embedding_model=embedding_model))
        print("输入内容：", user_input)

        # print("回复结果：", result["answer"])
        print("回复结果====>：", result)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"本轮问答耗时：{execution_time}秒")

    # 示例用法
    # start_time = time.time()  # 获取开始时间
    # result = """
    # Here is some text before the JSON data.
    # ```json
    # {
    #   "key": "value"
    # }```"""
    #
    # print(extract_json_from_llm_answer(result))
    # end_time = time.time()  # 获取结束时间
    # execution_time = end_time - start_time  # 计算运行时间
    # print(f"本轮过滤耗时：{execution_time}秒")

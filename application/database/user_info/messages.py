import time

from application.config import setting
from extend.mysql.sql import Sql


def clean_chat_history(chat_history):
    """一个确保大模型消息列表为标准格式的函数"""
    # # 如果列表为空或只有一个元素，则无需处理
    # if len(chat_history) < 1:
    #     return chat_history

    # 如果此时列表为空，则返回空列表
    if not chat_history:
        return chat_history

    # 确保第一个元素的 role 是 'user'
    while chat_history and chat_history[0]['role'] != 'user':
        chat_history.pop(0)

    # 确保最后一个元素的 role 是 'assistant'
    while chat_history[-1]['role'] != 'assistant':
        chat_history.pop()
        # 如果删除了最后一个元素，需要重新检查列表是否为空
        if not chat_history:
            return chat_history

    # 清理中间的元素，确保 'user' 和 'assistant' 交替出现
    i = 1
    while i < len(chat_history):
        # 如果当前元素和前一个元素 role 相同，则删除当前元素
        if chat_history[i]['role'] == chat_history[i - 1]['role']:
            chat_history.pop(i)
        else:
            i += 1

    return chat_history


def limit_chat_history(chat_history: list, limit: int):
    """一个限制历史记录条数的函数"""
    if len(chat_history) >= limit:
        return chat_history[-20:]
    else:
        return chat_history


# 获取用户消息
def get_user_message(user_handle):
    """一个传入用户id从数据库读取用户消息的函数"""
    set_sql = {
        'user': setting.user,
        'password': setting.password,
        'host': setting.host,
        'database': setting.database,
    }
    # 获取用户信息列表
    messages = Sql(prompt=set_sql).select_history(user_handle=user_handle)

    chat_history_list = []
    chat_history_str_list = []
    for msg in messages:
        role = "user" if msg["tny"] == 1 else "assistant"
        content = msg["content"]
        chat_history_list.append({
            "role": role,
            "content": content
        })
        role_str = "用户" if role == "user" else "你"
        chat_history_str_list.append(f'{role_str}：{content}')
    chat_history = chat_history_list[::-1]
    chat_history_str = chat_history_str_list[::-1]

    # 如果消息条数大于20条，只取20条
    limit_clean_history = limit_chat_history(chat_history, 20)
    limit_chat_history_str = limit_chat_history(chat_history_str[1:], 20)

    # 应保证消息列表第一条数据为user，最后一条消息为assistant
    # 确保消息列表为大模型标准格式
    clean_history = clean_chat_history(limit_clean_history)
    # print("chat_history>>>>>>>>>>", clean_history)
    # print("chat_history_str>>>>>>>>>>", chat_history_str[1:])

    return {"chat_history": clean_history, "chat_history_str": limit_chat_history_str}


if __name__ == "__main__":
    chat_history = [

        {'role': 'assistant', 'content': '欢迎进入'},
        {'role': 'user', 'content': '好的'},
        {'role': 'user', 'content': '有啥动漫'},
        {'role': 'assistant', 'content': '动漫企业申请流程吗？'},
        {'role': 'user', 'content': '想'},
        {'role': 'assistant', 'content': '比如税务申报、税务筹划还是税务咨询？'},
    ]
    # print("测试获取的用户数据：")
    start_time = time.time()  # 获取开始时间
    # cleaned_chat_history = clean_chat_history(chat_history)
    start_time1 = time.time()  # 获取开始时间
    ret = get_user_message("ihgPoc9526")
    print(ret['chat_history'])
    # print("输入内容：")
    # print("回复结果：", cleaned_chat_history)
    end_time = time.time()  # 获取结束时间
    execution_time = start_time1 - start_time  # 计算运行时间
    execution_time1 = end_time - start_time1  # 计算运行时间
    print(f"检查格式时间：{execution_time}秒")
    print(f"读取数据库时间：{execution_time}秒")

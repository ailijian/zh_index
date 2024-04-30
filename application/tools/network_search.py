# agently的网络搜索工具
import time
from application.agents.base_agent import BaseAgent  # 从base_agent中引入基础agent类BaseAgent

# 创建基础agent实例
# create_agent()方法默认使用文心4.0模型，默认从config中获取token，默认关闭debug，如果有需要，请自行传参
# create_agent(current_model="ERNIE", model="ernie-4.0", token=tokens.ERNIEBOT_ACCESS_TOKEN, is_debug=False)
agent = BaseAgent.create_agent(is_debug=True)


def search_query(question: str):
    """一个agently实现的，让大模型联网搜索回复的函数"""
    result = (
        agent
        .use_public_tools(["get_now", "search", ])
        .set_tool_proxy("http://127.0.0.1:7890")
        .input(question)
        .start()
    )
    return result


if __name__ == "__main__":
    while True:
        # chat_history = ""
        # chat_history_list = ["你好", "你好，有什么可以帮你？"]
        # chat_history = "客户：你好\n你：你好，有什么可以帮你？\n"
        user_input = input("请输入测试内容：")
        if user_input == "exit":
            break
        start_time = time.time()  # 获取开始时间
        result = search_query(user_input)
        print("输入内容：", user_input)
        print("回复结果：", result)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"本轮问答耗时：{execution_time}秒")

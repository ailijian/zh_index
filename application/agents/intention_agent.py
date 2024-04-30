# 路由agent，判断用户消息类型，选择对应的agent进行处理
import asyncio
import json
import time
from application.agents.base_agent import BaseAgent  # 从base_agent中引入基础agent类BaseAgent

# 创建基础agent实例
# create_agent()方法默认使用文心4.0模型，默认从config中获取token，默认关闭debug，如果有需要，请自行传参
# create_agent(current_model="ERNIE", model="ernie-4.0", token=tokens.ERNIEBOT_ACCESS_TOKEN, is_debug=False)
# agent = BaseAgent.create_agent(is_debug=True)


class IntentionAgent:
    """继承BaseAgent类，创建一个用于判断用户消息类的路由agent"""

    def __init__(self):
        pass

    # @staticmethod
    async def get_intention(self, user_input, chat_history_str, agent_id: str):
        """一个传入用户对话信息，输出销售阶段的函数"""
        start_time = time.time()  # 获取开始时间
        agent = BaseAgent.create_agent(agent_id=agent_id, is_debug=True)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"\n\n创建意图识别agent的时间为：{execution_time}秒\n\n")

        if chat_history_str and len(chat_history_str) > 0:
            chat_history_str = "\n".join(chat_history_str)
        else:
            chat_history_str = ""
        # 使用RouterAgent判断用户输入的意图
        user_intention = (
            await agent
            .instruct(
                "根据你和用户的历史对话记录，判断当前用户输入内容的意图，并总结出当前用户想要咨询的关键问题\n"
                f"```历史对话记录：\n{chat_history_str}\n```"
                f"[当前用户输入]：{user_input}\n"
            )
            .output({
                "intention": ("闲聊｜咨询", "从'闲聊','咨询'中选择一项作为你对[当前用户输入]意图的判断结果"),
                "topic": (
                    "str",
                    "如果{intention}==咨询，给出当前用户想要咨询的关键问题，否则请输出''\n"
                    "注意，你只需要按[输出要求]输出结果，不需要输出任何解释"),
            })
            # .output({
            #     "意图": (
            #         "str", f"务必从列表中选择一项作为你的判断结果，千万不能输出列表以外的阶段"),
            #     "是否准确": ("bool", "根据[处理规则]，判断{销售阶段}是否准确，准确请输出true"),
            #     "重选结果": ("str", "如果{是否准确}==false，根据[处理规则]，重新输出判断结果，反之，输出''\n"
            #                         "注意，你只需要根据[输出要求]输出结果，不需要输出任何解释，不要着急，让我们一步步思考后开始输出"),
            # })
            # .start()
            .start_async()
        )
        # if not user_intention["是否准确"]:
        #     return user_intention["重选结果"]
        # if 'json' in str(user_intention):
        #     user_intention = user_intention.replace("```", "").replace("json", "")
        #     user_intention = json.loads(user_intention)
        # print('=============>用户意图：{}==================》'.format(user_intention))
        return user_intention


# 实例化路由agent
intention_agent = IntentionAgent()

if __name__ == "__main__":
    while True:
        # chat_history = ""
        # chat_history_list = ["你好", "你好，有什么可以帮你？"]
        # chat_history = "客户：你好\n你：你好，有什么可以帮你？\n"
        user_input = input("请输入测试内容：")
        if user_input == "exit":
            break
        start_time = time.time()  # 获取开始时间
        result = asyncio.run(intention_agent.get_intention(user_input))
        print("输入内容：", user_input)
        print("选择结果：", result)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"本轮选择耗时：{execution_time}秒")

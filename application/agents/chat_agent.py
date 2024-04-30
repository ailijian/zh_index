# 聊天agent
import asyncio
import time
from application.agents.base_agent import BaseAgent  # 从base_agent中引入基础agent类BaseAgent

# 创建基础agent实例
# create_agent()方法默认使用文心4.0模型，默认从config中获取token，默认关闭debug，如果有需要，请自行传参
# create_agent(current_model="ERNIE", model="ernie-4.0", token=tokens.ERNIEBOT_ACCESS_TOKEN, is_debug=False)
# agent = BaseAgent.create_agent(agent_id, is_debug=True)


class ChatAgent(BaseAgent):
    """继承BaseAgent类，创建一个用于闲聊的agent"""

    def __init__(self):
        super().__init__()  # BaseAgent默认携带企业介绍、角色信息设定、销售信息设定，如果不需要用到父类的属性，就不用继承

    # @staticmethod
    async def chat(self, user_input: str, chat_history: str, agent_id: str):
        """一个输入prompt获得agent回复的函数"""
        start_time = time.time()  # 获取开始时间
        agent = BaseAgent.create_agent(agent_id=agent_id, is_debug=True)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"\n\n创建闲聊agent的时间为：{execution_time}秒\n\n")
        result = (
            await agent
            # 设定全局信息
            # .general("企业简介", self.brand_introduction)
            # .general("你的任务", self.service_items)
            # 设定角色信息
            .role(self.system_role)
            .input(user_input)
            # .chat_history(chat_history)
            .set_request_prompt("chat_history", chat_history)
            # .instruct(
            #     "在回复时遵循以下顺序进行表达：\n" +
            #     f"首先，根据用户输入内容给出回应语或emoji表情，例如{self.role_initial_response_list}\n" +
            #     "然后，言简意赅的给出你对用户输入内容的回应\n" +
            #     "最后，言简意赅的围绕你的任务给出接下来可能可以探讨的话题的建议\n" +
            #     "注意应该使用口语化表达，不使用比如'首先...其次...再次'之类的结构化表达方法"
            # )
            .output(
                {
                    "response": (
                        {
                            "topic": (
                                "str", "根据历史对话记录和当前[输入]内容，判断用户想要表达的关键问题"),
                            # "initial": (
                            #     "str", f"根据用户输入内容给出回应语或emoji表情，例如{self.role_initial_response_list}"),
                            "answer": ("str", "结合{topic}，言简意赅的对[输入]内容进行回复"),
                            # "suggestion": ("str", "你对接下来可以探讨的话题的建议，如果没有则输出''"),
                            "relative": ("str",
                                         "根据{topic}、{answer}和[输入]内容，言简意赅的给出接下来可以探讨的话题的建议，可以延续当前话题，"
                                         "也可以围绕你的任务开启新话题，例如“请问您想了解XX吗？”，如果{answer}中已经给出建议了，请输出''"),
                        }),
                }
            )
            # .start()
            .start_async()
        )
        # end_time = time.time()  # 获取结束时间
        # execution_time = end_time - start_time  # 计算运行时间
        # print(f"\n\n本轮闲聊回答的时间为：{execution_time}秒\n\n")
        return result


if __name__ == "__main__":
    # 实例化聊天agent
    chat_agent = ChatAgent()
    while True:
        # chat_history = ""
        # chat_history_list = ["你好", "你好，有什么可以帮你？"]
        # chat_history = "客户：你好\n你：你好，有什么可以帮你？\n"
        user_input = input("请输入测试内容：")
        if user_input == "exit":
            break
        start_time = time.time()  # 获取开始时间
        result = asyncio.run(chat_agent.chat(user_input))
        print("输入内容：", user_input)
        print("回复结果：", result)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"本轮问答耗时：{execution_time}秒")

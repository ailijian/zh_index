# 检索agent
import asyncio
import time
from application.agents.base_agent import BaseAgent  # 从base_agent中引入基础agent类BaseAgent
from application.RAG.vector_search import retrieval_results
from application.agents.intention_agent import IntentionAgent

# 创建基础agent实例
# create_agent()方法默认使用文心4.0模型，默认从config中获取token，默认关闭debug，如果有需要，请自行传参
# create_agent(current_model="ERNIE", model="ernie-4.0", token=tokens.ERNIEBOT_ACCESS_TOKEN, is_debug=False)
# agent = BaseAgent.create_agent(is_debug=True)


class RetrieveAgent(BaseAgent):
    """继承BaseAgent类，创建一个用于问答的agent"""

    def __init__(self):
        super().__init__()  # BaseAgent默认携带企业介绍、角色信息设定、销售信息设定，如果不需要用到父类的属性，就不用继承

    # @staticmethod
    async def retrieve(self, user_input: str, chat_history: str, retrieve_results: str, intention_topic: str, agent_id: str):
        """一个输入prompt获得agent回复的函数"""
        # start_time = time.time()  # 获取开始时间
        start_time = time.time()  # 获取开始时间
        agent = BaseAgent.create_agent(agent_id=agent_id, is_debug=True)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"\n\n创建问答agent的时间为：{execution_time}秒\n\n")

        result = (
            await agent
            # 设定全局信息
            # .general("企业简介", self.brand_introduction)
            # .general("你的任务", self.service_items)
            # 设定角色信息
            .role(self.system_role)
            .input(f"{user_input}\n\n```[知识库资料]：\n{retrieve_results}```")
            # .chat_history(chat_history)
            .set_request_prompt("chat_history", chat_history)
            # .output(
            #     {
            #         "answers": (
            #             [{
            #                 "question_topic": ("str", "根据{input}判断关键问题"),
            #                 "answer": ("str", "你对{question_topic}的直接回答"),
            #                 "suggestion": ("str", "你对回答/解决{question_topic}的进一步行动建议，如果没有可以输出''"),
            #                 "relative_questions": ([("str", "与{question_topic}相关的可以探讨的其他问题")], "不超过3个")
            #             }],
            #             "根据{input}对用户提问进行回答，用户有多个提问，应该在{answers}中拆分成多个{question_topic}以及对应的回答"
            #         )
            #     }
            # )
            .output(
                {
                    "response": (
                        [{
                            "is_ok": (
                                "bool",
                                "根据历史对话记录、当前用户[输入]的内容以及[知识库资料]，判断用户的问题是否完整齐备，能够执行查询"
                                "准确请输出true，反之，输出false"),
                            "topic": ("str", f"根据历史对话记录、当前[输入]的内容以及初次关键问题总结：“{intention_topic}”，再次总结用户想要咨询的关键问题"),
                            "is_know": (
                                "bool",
                                "判断[知识库资料]中是否有{topic}问题对应的答案，如果有，请输出true，反之，输出false"),
                            "initial": (
                                "str",
                                "如果{is_ok}==false，请结合[知识库资料]询问用户想要了解的具体问题，例如“请问您具体想了解XXX呢？”，否则请输出''"),
                            "answer": (
                                "str", "如果{is_know}==true，请务必根据[知识库资料]，言简意赅的对[知识库资料]中有答案的{topic}进行回复，"
                                       "没有答案的{topic}则向用户说明该问题知识库中没有找到相关资料\n"
                                       "如果{is_know}==false，请不要回复，应该告诉用户“关于XXX问题，知识库中没有找到相关资料~”\n"
                            ),
                            "relative": (
                                "str",
                                # "根据历史对话记录、{answer}和用户当前[输入]内容，推测用户想要了解的更多信息，并言简意赅的给出接下来可以探讨的话题的建议，"
                                "根据历史对话记录、{answer}和用户当前[输入]内容，推测用户想要了解的更多信息，并言简意赅的给出建议，"
                                "可以延续当前话题，也可以围绕你的任务开启新话题，例如“您看需要了解XX吗？”\n"),
                        }],
                        # "注意，如果用户有多个提问，应该在{response}中拆分成多个{topic}以及对应的回答\n"  # {initial}和{answer}
                        "请仔细检查{response}中的{is_ok}、{topic}、{is_know}判断是否准确，不准确请更正后再回复\n"  # {initial}和{answer}
                        "不要着急，请一步步思考后输出答案"
                    )
                }
            )
            # .on_delta(lambda data: {
            #     print('流式输出测试=====================》{}'.format(data))
            # })
            # .start()
            .start_async()
        )
        # end_time = time.time()  # 获取结束时间
        # execution_time = end_time - start_time  # 计算运行时间
        # print(f"大模型回答的时间为：{execution_time}秒")
        return result


if __name__ == "__main__":
    # 实例化意图agent
    intention_agent = IntentionAgent()
    # 实例化检索agent
    retrieve_agent = RetrieveAgent()
    while True:
        # chat_history = ""
        # chat_history_list = ["你好", "你好，有什么可以帮你？"]
        # chat_history = "客户：你好\n你：你好，有什么可以帮你？\n"
        user_input = input("请输入测试内容：")
        if user_input == "exit":
            break
        start_time = time.time()  # 获取开始时间
        # 意图识别
        user_intention = asyncio.run(intention_agent.get_intention(user_input))
        # 关键问题检索
        retrieve_results = retrieval_results(user_input + user_intention["topic"], 3)
        # 回答
        result = asyncio.run(retrieve_agent.retrieve(user_input, retrieve_results, user_intention["topic"]))
        print("输入内容：", user_input)
        print("检索内容：", retrieve_results)
        print("回复结果：", result)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"本轮问答耗时：{execution_time}秒")

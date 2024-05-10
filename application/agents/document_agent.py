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


class DocumentAgent:
    """继承BaseAgent类，创建一个用于问答的agent"""

    def __init__(self):
        super().__init__()  # BaseAgent默认携带企业介绍、角色信息设定、销售信息设定，如果不需要用到父类的属性，就不用继承

    # @staticmethod
    async def extract(self, documents: list):
        """一个抽取文档关键信息的函数，例如主题、章节等"""
        # start_time = time.time()  # 获取开始时间
        start_time = time.time()  # 获取开始时间
        agent = BaseAgent.create_agent(model="ernie-3.5", is_debug=True)
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"\n\n创建文档主题抽取agent的时间为：{execution_time}秒\n\n")

        num = len(documents)
        documents_list = [f"第{i+1}段：\n{document}\n" for i, document in enumerate(documents)]

        # documents_list = []
        # for i, document in enumerate(documents):
        #     documents_list.append(f"第{i}段：\n{document}\n")
        for document in documents_list:
            print("打印document：\n", document)
            print("############################")

        result = (
            await agent
            # .instruct(
            #     f"你的任务是处理文本段，我把一份文档切割成了多个文本段，本次我将传{num}个待处理的文本段给你，你需要对这些文本段做如下处理："
            #     f"1.从本次{num}个待处理的文本段中抽取标题、发文时间、目录、章节\n"
            #     "2.对每个文本段进行总结\n"
            #     "3.判断相邻文本段之间是否需要合并\n"
            #     f"```待处理的文本段：\n{''.join(documents_list)}```"
            #     f"注意，每个文本段之间少量的重叠内容是为了增强文本段之间的关联性，在抽取文本段里的信息时，应忽略这部分重叠内容")
            .input(
                f"```待处理的文本段：\n{''.join(documents_list)}```"
                "注意，以上每个文本段之间少量的重叠内容是为了增强文本段之间的关联性，在抽取文本段里的信息时，应忽略这部分重叠内容")
            .output({
                "title": ("str", "从待处理的文本段中抽取文档标题，如果没有标题，则输出''"),
                "release_time": (
                    "str",
                    "从待处理的文本段中抽取文档的发文时间，如果没有时间，则输出''\n"
                    "注意，你需要抽取的是发布文档的时间，实施时间、实行时间等非文档发布时间不需要抽取"),
                "directory": ("list", f"从待处理的文本段中抽取目录，并为其中的{num}个文本段分别添加对应的目录，以列表格式输出，例如['目录一', '目录一' ,'目录一', '目录二']，"
                                      "请注意，章节是目录的子集，一个目录可能包含多个章节，但一个章节不能包含多个目录"),
                "chapter": ("list",
                            f"从待处理的文本段中抽取章节，并为其中的{num}个文本段分别添加对应的章节，以列表格式输出。如果文本段里没有明确的章节划分，"
                            f"请对待处理的文本段进行分析并生成章节后再为其中的{num}个文本段添加章节，例如['章节一', '章节二' ,'章节二', '章节三']，"
                            "请注意，章节是目录的子集，一个目录可能包含多个章节，但一个章节不能包含多个目录"),
                "summary": (
                    "list", f"请对待处理文本段中的{num}个文本段分别进行总结，以列表格式输出，例如['总结一', '总结二' ,'总结三', '总结四']"
                ),
                "is_merge": (
                    "list",
                    "请根据以上所有信息，判断下一个文本段是否包含了上一个文本段缺失的内容，如果是，请将这两个文本段进行合并以保证内容完整。"
                    "以下是输出示例：\n"
                    "合并第1段和第2段，请输出['1','2']\n"
                    "合并第2段和第3段，请输出['2','3']\n"
                    "合并第1段、第2段和第3段，请输出['1','2','3']\n"
                    "第1段、第2段，第3段和第4段分别合并，请输出[['1','2'],['3','4']]\n"
                    "如果只有1段文本，则输出''"),
            })
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

    async def extract_document_topic(self, documents: list):
        """将文档分段传入文档信息抽取agent，获取相关信息"""
        topic_extractor = []
        # 设置初始索引、窗口大小和步长
        start_index = 0
        window_size = 4
        step = 3  # 重叠一个元素，所以步长为3
        # 当起始索引加上窗口大小不超过文档列表长度时，继续循环
        while start_index + window_size <= len(documents) - 1:
            # 从当前索引开始取window_size个元素
            customer_documents = documents[start_index:start_index + window_size]

            # 调用extract函数并获取结果
            extract_result = await self.extract(customer_documents)

            # 根据需要处理extract_result
            print(f"Extract result: {extract_result}")
            topic_extractor.append(extract_result)

            # 更新索引，准备下一次迭代
            start_index += step

            # 处理剩余的元素（如果有的话）
        if start_index < len(documents) - 1:
            customer_documents = documents[start_index:]
            # 调用extract函数并获取结果
            extract_result = await self.extract(customer_documents)
            print(f"Extract result for remaining documents: {extract_result}")
            topic_extractor.append(extract_result)

        return topic_extractor


if __name__ == "__main__":
    # 实例化文档信息抽取agent
    document_agent = DocumentAgent()
    documents = [
        "冯冰心",
        "杨雨竹",
        "蔡娜",
        "张小华",
        "陈晨",
        "马嘉莉",
        "余蒙",
    ]

    start_time = time.time()  # 获取开始时间

    # 关键信息抽取
    result = asyncio.run(document_agent.extract_document_topic(documents))
    print("输入内容：", documents)
    print("抽取结果：", result)
    end_time = time.time()  # 获取结束时间
    execution_time = end_time - start_time  # 计算运行时间
    print(f"本轮问答耗时：{execution_time}秒")

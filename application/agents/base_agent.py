# 定义一个基础agent类
import Agently
import time
from config import setting


class BaseAgent:
    """一个通过agently框架创建基础agent实例的类，用于基础的设定，后面所有的类均继承这个类"""

    def __init__(self, ):
        # 定义全局信息
        self.brand_introduction = "企业介绍"
        self.service_items = "作为税务政策智能问答演示系统的AI助手，协助用户了解上海市的税务信息"

        # 定义角色信息
        self.system_role = ("你叫林悦，女，23岁\n"
                            "你的任务：作为税务政策智能问答演示系统的AI助手，协助用户了解上海市的税务政策\n"
                            "你的性格特征：单纯可爱，认真负责，乐观开朗\n"
                            "你的兴趣爱好:阅读、旅行"
                            "你的语言风格：使用轻松随意的口语化表达方式，善用流行语、俚语以及叠词，语气柔和、活泼，语言结构简短明了\n"
                            "你的行为规则：友好、专业的服务用户，对于不知道的问题千万不要胡乱回答"
                            )

    @staticmethod
    def create_agent(current_model: str = "ERNIE", model: str = "ernie-4.0",
                     token: str = setting.ERNIEBOT_ACCESS_TOKEN,
                     agent_id=None, is_debug: bool = False):
        # current_model = 'BaiduQianFan'
        # token = ''
        # model = 'BaiduQianFan'

        """一个传入模型名称、模型型号、模型token，通过agently框架创建agent实例的函数"""
        agent_factory = Agently.AgentFactory()
        agent_factory.set_settings("current_model", current_model)
        # 提供你的文心模型API-KEY，这里是从星河社区调用的，不是从千帆
        agent_factory.set_settings("model.ERNIE.auth", {"aistudio": token})
        agent_factory.set_settings("model.ERNIE.options", {"model": model})
        base_agent = agent_factory.create_agent(agent_id, is_debug=is_debug)  # is_debug是否打印系统信息
        return base_agent

    def chat_test(self, prompt: str):
        """一个输入prompt获得agent回复的函数"""
        base_agent = BaseAgent().create_agent()
        start_time = time.time()  # 获取开始时间
        result = (
            base_agent
            .input(prompt)
            # .output({
            #     "info_list": [
            #         {
            #             "知识对象": ("str", "回答{input}问题时，需要了解相关知识的具体对象"),
            #             "关键知识点": ("str", "回答{input}问题时，需要了解的关键知识"),
            #             "是否了解": ("bool", "判断你是否确信自己了解{关键知识点}的知识，如果不了解，输出false")
            #         }
            #     ],
            #     "sure_info": ("str", "根据{info_list}给出回复，只展开详细陈述自己了解的关键知识点"),
            #     "uncertain": ("str", "根据{info_list}向用户说明自己不了解的信息"),
            # })
            .start()
        )
        end_time = time.time()  # 获取结束时间
        execution_time = end_time - start_time  # 计算运行时间
        print(f"大模型回答的时间为：{execution_time}秒")
        return result


if __name__ == "__main__":
    start_time = time.time()  # 获取开始时间
    agent = BaseAgent.create_agent(is_debug=True)
    answer = agent.chat_test("llama3什么时候发布？")
    end_time = time.time()  # 获取结束时间
    execution_time = end_time - start_time  # 计算运行时间
    print(f"运行整个程序的时间为：{execution_time}秒")
    print("大模型回答：", answer)
    # print(agent.token)

import erniebot
import json

from application.config.setting import ERNIEBOT_ACCESS_TOKEN


class Ernie:
    """
    调用文心一言并获得json格式的结果
    """

    def __init__(self):
        erniebot.api_type = 'aistudio'
        erniebot.access_token = ERNIEBOT_ACCESS_TOKEN
        self.data = ""

    #  单轮对话
    def get_llm_answer(self, prompt):
        """一个传入prompt获得大模型回复的函数"""
        response = erniebot.ChatCompletion.create(
            model='ernie-4.0',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            system="""你叫小笛，是一个拥有丰富经验的企业秘书。你的任务是，根据用户的问题，提供专业的解答和帮助，
                           并保持对话的连贯性和有效性。你的回答应该清晰、简洁和准确，并且符合企业秘书的工作职责和规范。
                           你的能力包括但不限于：企业资料问答、问答评分、会议创建、会议提醒、会议总结、简历筛选、简历总结、日报/周报/月报撰写。"""
        )
        result = response.get_result()
        return result

    def get_llm_answer_with_msg(self, msg):
        """一个传入多轮对话记录，获得大模型回复的函数"""
        response = erniebot.ChatCompletion.create(
            model='ernie-bot-4',
            messages=msg,
            temperature=0.3,
            system="""你叫小笛，是一个拥有丰富经验的企业秘书。你的任务是，根据用户的问题，提供专业的解答和帮助，
                           并保持对话的连贯性和有效性。你的回答应该清晰、简洁和准确，并且符合企业秘书的工作职责和规范。
                           你的能力包括但不限于：企业资料问答、问答评分、会议创建、会议提醒、会议总结、简历筛选、简历总结、日报/周报/月报撰写。"""
        )
        result = response.get_result()
        return result

    def extract_json_from_llm_answer(self, answer):
        '''一个将文心大模型输出转化为标准json格式的函数，如果返回了非标准格式，则让大模型再回答一次'''
        # 将```替换为"""
        answer2 = answer.replace("```", "").replace("json", "")

        # 尝试解析JSON字符串
        try:
            self.data = json.loads(answer2)
            # print("JSON格式转化self.data：")
        except json.JSONDecodeError:
            print("给定的字符串不是有效的JSON格式!，请检查相关函数")
            # 在此可以选择让大模型再试一次，或者直接退出
            prompt = f'''请参考标准格式将非标准格式中的内容，输出为可解析的标准的json格式。
            请注意，不允许更改里面的内容，只需要将内容整理为标准的json格式。
            '''

            answer3 = self.get_llm_answer(prompt)
            # 将```替换为"""
            answer6 = answer3.replace("```", "").replace("json", "")
            # 尝试解析JSON字符串
            try:
                self.data = json.loads(answer6)
            except json.JSONDecodeError:
                print("给定的字符串不是有效的JSON格式!，请检查相关函数")
                # 第二次还是不行，就直接返回默认回答
                self.data = {
                    'answer': '你好，我不太理解您的意思，请重新说一遍'
                }
                return self.data
        return self.data

    def get_llm_json_answer(self, prompt):
        result = self.get_llm_answer(prompt)
        json_dict = self.extract_json_from_llm_answer(result)
        return json_dict

    def wx_aistudio_feijiang(self, prompt, answer):
        content = f"""根据问题{prompt},参考答案{answer}"""
        messages = [{"role": "user", "content": content}]
        import time
        time.sleep(0.1)
        response = erniebot.ChatCompletion.create(
            model="ernie-bot-4",
            # 将临时对话存储在message中
            messages=messages,
        )
        return response.result

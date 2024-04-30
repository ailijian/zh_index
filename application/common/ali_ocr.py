from http import HTTPStatus
from config.setting import ERNIEBOT_ACCESS_TOKEN
import dashscope

dashscope.api_key = ERNIEBOT_ACCESS_TOKEN


def simple_multimodal_conversation_call(file_path):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": file_path},
                {"text": f"""
                    你现在的任务是根据文字识别的所有内容，为我整理图片里面的信息。
                    我为你提供了识别出来的图片内容。顺序在原始图片中从左至右、从上至下。
                    请注意文字识别结果可能存在长句子换行被切断、不合理的分词、对应错位等问题，你需要结合上下文语义以及我提供给你的信息进行综合判断.以抽取准确的关键信息。
                    最后输出的内容要节俭，而且要比较全，不能结构化展示结果，要以字符串的形式返回。
                     """
                 }
            ],
            "top_k": "80",
            "top_p": "0.6"

        }
    ]
    response = dashscope.MultiModalConversation.call(model='qwen-vl-plus', messages=messages)

    if response.status_code == HTTPStatus.OK:
        return response.output.get("choices")[0].get("message").get("content")[0].get("text")
    else:
        return "图片识别失败"

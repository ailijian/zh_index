import erniebot
from application.config.setting import ERNIEBOT_ACCESS_TOKEN
from typing import Optional, List, Mapping, Any
from llama_index.core import SimpleDirectoryReader, SummaryIndex, VectorStoreIndex
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class Ernie(CustomLLM):
    context_window: int = 5096
    num_output: int = 2048
    model_name: str = "ERNIE"
    dummy_response: str = "My response"

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        erniebot.api_type = 'aistudio'
        erniebot.access_token = ERNIEBOT_ACCESS_TOKEN
        response = erniebot.ChatCompletion.create(
            model='ernie-4.0',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.95,
            # system='',
            stream=False,
        )
        self.dummy_response = response.get_result()
        return CompletionResponse(text=self.dummy_response)

    @llm_completion_callback()
    def stream_complete(
            self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        erniebot.api_type = 'aistudio'
        erniebot.access_token = ERNIEBOT_ACCESS_TOKEN
        response = erniebot.ChatCompletion.create(
            model='ernie-4.0',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.95,
            # system='',
            stream=True,
        )
        self.dummy_response = response.get_result()
        response_stream = ""
        for token in self.dummy_response:
            response_stream += token
            yield CompletionResponse(text=response_stream, delta=token)


if __name__ == '__main__':
    # 设定LLM
    Settings.llm = Ernie()

    # 设定embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=r"E:\上海笛量\models\bge-base-zh-v1.5",
        # device="cuda",
        # normalize=True,  # 设置为True就是计算余弦相似度
        query_instruction="为这个句子生成表示以用于检索相关文章："
    )

    # 加载文档
    documents = SimpleDirectoryReader(r"E:\上海笛量\project\zh_index\application\database\enterprise_info\pdf").load_data()
    index = SummaryIndex.from_documents(documents)
    index1 = VectorStoreIndex.from_documents(documents)

    # 输入查询语句获得回答
    query_engine = index.as_query_engine()
    answer = query_engine.query("涉税专业服务基本准则（试行）的发布日期是什么时候？")
    prompts_dict = query_engine.get_prompts()
    print("prompt：", list(prompts_dict.keys()))
    print("prompt1：", list(prompts_dict.values()))
    print("prompt2：", list(prompts_dict))
    # query_engine1 = index1.as_query_engine()
    # answer1 = query_engine1.query("涉税专业服务基本准则（试行）的发布日期是什么时候？")
    print("检索结果：", answer)
    # print("检索结果1：", answer1)

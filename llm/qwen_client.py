import os
from openai import OpenAI
from .base_llm import BaseLLM


class QwenClient(BaseLLM):
    def __init__(self, api_key: str | None = None, model: str = "qwen-plus"):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
        self.model = model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    def name(self) -> str:
        return f"Qwen({self.model})"

from .base_agent import BaseAgent


class ReviewAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("ReviewAgent", llm)

    def get_system_prompt(self) -> str:
        return """你是一个代码审查Agent。你的任务是审查前一个Agent生成的设计文档或代码，判断其质量。

你需要输出以下格式：
PASS 或 REJECT

如果是 PASS，在下一行简要说明通过原因。
如果是 REJECT，在下一行说明问题所在，并给出改进建议。

只输出 PASS/REJECT 和简要说明，不要输出其他内容。"""

    def process(self, input_data: str) -> str:
        prompt = f"请审查以下内容的质量：\n\n{input_data[:2000]}"
        return self.call_llm(prompt)

    def is_passed(self, result: str) -> bool:
        return result.strip().upper().startswith("PASS")

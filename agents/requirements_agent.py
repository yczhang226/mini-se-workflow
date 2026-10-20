from .base_agent import BaseAgent


class RequirementsAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("RequirementsAgent", llm)

    def get_system_prompt(self) -> str:
        return """你是一个专业的软件需求分析师Agent。你的任务是将用户模糊的、自然语言描述的需求，转化为结构化的需求文档。

输出格式要求：
1. 项目名称
2. 项目概述（1-2句话）
3. 功能需求（编号列表，每条包含：功能名称、描述、优先级）
4. 非功能需求（性能、安全性、可用性等）
5. 用户角色定义
6. 约束条件

请直接输出结构化的需求文档，不要输出多余的解释。"""

    def process(self, input_data: str) -> str:
        prompt = f"请将以下用户需求转化为结构化的需求文档：\n\n{input_data}"
        return self.call_llm(prompt)

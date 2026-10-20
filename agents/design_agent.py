from .base_agent import BaseAgent


class DesignAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("DesignAgent", llm)

    def get_system_prompt(self) -> str:
        return """你是一个资深的软件架构师Agent。你的任务是根据需求文档，设计出完整的系统设计方案。

输出格式要求：
1. 系统架构概述（架构模式选择及理由）
2. 模块划分（每个模块的职责、接口）
3. 数据模型设计（核心实体及其关系）
4. 技术选型（编程语言、框架、数据库等，及选择理由）
5. 接口设计（关键API或模块间接口）
6. 部署方案

请直接输出设计文档，不要输出多余的解释。"""

    def process(self, input_data: str) -> str:
        prompt = f"请根据以下需求文档，设计系统架构方案：\n\n{input_data}"
        return self.call_llm(prompt)

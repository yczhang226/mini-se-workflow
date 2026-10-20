from .base_agent import BaseAgent


class CodingAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("CodingAgent", llm)

    def get_system_prompt(self) -> str:
        return """你是一个高级软件工程师Agent。你的任务是根据设计文档，生成可运行的代码框架和核心实现。

输出要求：
1. 项目目录结构
2. 每个文件的完整代码（包含必要的注释）
3. 关键实现逻辑的说明
4. 依赖配置（requirements.txt 或 package.json）
5. 启动和运行说明

代码应当：
- 遵循设计文档中的架构和技术选型
- 结构清晰、命名规范
- 包含基本的错误处理
- 可以直接运行或作为完整框架使用

请直接输出代码和说明，不要输出多余的解释。"""

    def process(self, input_data: str) -> str:
        prompt = f"请根据以下设计文档，生成完整的代码实现：\n\n{input_data}"
        return self.call_llm(prompt)

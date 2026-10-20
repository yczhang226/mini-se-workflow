import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DEEPSEEK_API_KEY, LLM_PROVIDER, LLM_MODEL, OUTPUT_DIR
from llm import DeepSeekClient, QwenClient
from agents import RequirementsAgent, DesignAgent, CodingAgent
from workflow import Orchestrator


def create_llm():
    if LLM_PROVIDER == "deepseek":
        return DeepSeekClient(api_key=DEEPSEEK_API_KEY, model=LLM_MODEL)
    return QwenClient(api_key=os.getenv("DASHSCOPE_API_KEY", ""), model=LLM_MODEL)


def main():
    llm = create_llm()

    requirements_agent = RequirementsAgent(llm)
    design_agent = DesignAgent(llm)
    coding_agent = CodingAgent(llm)

    orchestrator = Orchestrator()
    orchestrator.add_agent(requirements_agent)
    orchestrator.add_agent(design_agent)
    orchestrator.add_agent(coding_agent)

    user_input = "开发一个Python计算器Web API，支持加减乘除四则运算，使用Flask框架"
    print(f"输入需求: {user_input}\n")

    result = orchestrator.run(user_input)

    if result["success"]:
        orchestrator.save_outputs(OUTPUT_DIR, result["results"])
        print("\n简单演示完成!")
    else:
        print(f"\n演示失败: {result['error']}")


if __name__ == "__main__":
    main()

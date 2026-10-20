import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DEEPSEEK_API_KEY, LLM_PROVIDER, LLM_MODEL, OUTPUT_DIR
from llm import DeepSeekClient, QwenClient
from agents import RequirementsAgent, DesignAgent, CodingAgent, ReviewAgent
from workflow import Orchestrator


def create_llm():
    if LLM_PROVIDER == "deepseek":
        return DeepSeekClient(api_key=DEEPSEEK_API_KEY, model=LLM_MODEL)
    return QwenClient(api_key=os.getenv("DASHSCOPE_API_KEY", ""), model=LLM_MODEL)


def main():
    llm = create_llm()

    requirements_agent = RequirementsAgent(llm)
    design_agent = DesignAgent(llm)
    review_agent = ReviewAgent(llm)
    coding_agent = CodingAgent(llm)

    orchestrator = Orchestrator()

    # 1. 需求分析（必执行，失败重试2次）
    orchestrator.add_agent(requirements_agent, max_retries=2)

    # 2. 设计（必执行，失败重试2次）
    orchestrator.add_agent(design_agent, max_retries=2)

    # 3. 审查（条件分支：仅在设计完成后执行）
    orchestrator.add_agent(
        review_agent,
        max_retries=1,
        condition=lambda results: "DesignAgent" in results,
    )

    # 4. 编码（必执行，失败重试2次）
    orchestrator.add_agent(coding_agent, max_retries=2)

    user_input = "开发一个Python命令行计算器，支持加减乘除和括号表达式解析"
    print(f"输入需求: {user_input}\n")
    print("=" * 60)
    print("高级特性演示: 条件分支 + 错误重试 + 执行计时")
    print("=" * 60 + "\n")

    result = orchestrator.run(user_input)

    print("\n" + "=" * 60)
    if result["success"]:
        print("Workflow 执行成功!")
        orchestrator.save_outputs(OUTPUT_DIR, result["results"])
        print(f"\n产出物已保存到: {OUTPUT_DIR}/")
    else:
        print(f"Workflow 执行失败: {result['error']}")

    print("\n--- 执行计时 ---")
    for name, t in result["timing"].items():
        print(f"  {name}: {t}s")
    if result.get("total_time"):
        print(f"  总计: {result['total_time']}s")

    print("\n--- Agent 状态 ---")
    for name, info in result["state"]["agents"].items():
        if info["status"] == "completed":
            icon = "[OK]"
        elif info["status"] == "idle":
            icon = "[--]"
        else:
            icon = "[X]"
        print(f"  {icon} {name}: {info['status']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import DEEPSEEK_API_KEY, DASHSCOPE_API_KEY, LLM_PROVIDER, LLM_MODEL, OUTPUT_DIR
from llm import QwenClient, DeepSeekClient
from agents import RequirementsAgent, DesignAgent, CodingAgent
from workflow import Orchestrator


def create_llm():
    if LLM_PROVIDER == "deepseek":
        if not DEEPSEEK_API_KEY:
            print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
            sys.exit(1)
        return DeepSeekClient(api_key=DEEPSEEK_API_KEY, model=LLM_MODEL)
    elif LLM_PROVIDER == "qwen":
        if not DASHSCOPE_API_KEY:
            print("错误: 请设置 DASHSCOPE_API_KEY 环境变量")
            sys.exit(1)
        return QwenClient(api_key=DASHSCOPE_API_KEY, model=LLM_MODEL)
    else:
        print(f"错误: 不支持的 LLM_PROVIDER: {LLM_PROVIDER}")
        sys.exit(1)


def main():
    llm = create_llm()

    print("=" * 60)
    print("  Mini SE Workflow - 需求 → 设计 → 编码")
    print(f"  LLM: {llm.name()}")
    print("=" * 60)
    print()

    user_input = input("请输入你的软件需求（直接回车使用示例需求）:\n> ").strip()

    if not user_input:
        user_input = (
            "开发一个命令行待办事项管理工具，支持添加任务、完成任务、"
            "删除任务、列出所有任务、按优先级筛选。数据保存在本地JSON文件中。"
        )
        print(f"\n使用示例需求: {user_input}\n")

    requirements_agent = RequirementsAgent(llm)
    design_agent = DesignAgent(llm)
    coding_agent = CodingAgent(llm)

    orchestrator = Orchestrator()
    orchestrator.add_agent(requirements_agent)
    orchestrator.add_agent(design_agent)
    orchestrator.add_agent(coding_agent)

    print("\n" + "-" * 60)
    print("开始执行 Workflow...")
    print("-" * 60 + "\n")

    result = orchestrator.run(user_input)

    print("\n" + "=" * 60)
    if result["success"]:
        print("Workflow 执行成功!")
        orchestrator.save_outputs(OUTPUT_DIR, result["results"])
        print(f"\n产出物已保存到: {OUTPUT_DIR}/")
    else:
        print(f"Workflow 执行失败: {result['error']}")
    print("=" * 60)

    print("\n--- 执行状态 ---")
    for name, info in result["state"]["agents"].items():
        status_icon = "[OK]" if info["status"] == "completed" else "[X]"
        print(f"  {status_icon} {name}: {info['status']}")


if __name__ == "__main__":
    main()

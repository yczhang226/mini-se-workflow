import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DEEPSEEK_API_KEY, LLM_PROVIDER, LLM_MODEL
from llm import DeepSeekClient, QwenClient
from agents import RequirementsAgent, DesignAgent, CodingAgent
from workflow.message import Message, MessageType


def create_llm():
    if LLM_PROVIDER == "deepseek":
        return DeepSeekClient(api_key=DEEPSEEK_API_KEY, model=LLM_MODEL)
    return QwenClient(api_key=os.getenv("DASHSCOPE_API_KEY", ""), model=LLM_MODEL)


def main():
    llm = create_llm()

    requirements_agent = RequirementsAgent(llm)
    design_agent = DesignAgent(llm)
    coding_agent = CodingAgent(llm)

    user_input = "开发一个学生成绩管理系统，支持录入成绩、查询成绩、统计平均分"

    print("=" * 50)
    print("分步演示 - Mini SE Workflow")
    print("=" * 50)

    # Step 1: 需求分析
    print("\n[Step 1] 需求Agent 处理中...")
    msg1 = Message(
        sender="User",
        receiver="RequirementsAgent",
        msg_type=MessageType.TASK,
        content=user_input,
    )
    resp1 = requirements_agent.handle_message(msg1)
    print(f"需求Agent 状态: {resp1.msg_type.value}")
    print(f"产出预览:\n{resp1.content[:300]}...\n")

    # Step 2: 系统设计
    print("[Step 2] 设计Agent 处理中...")
    msg2 = Message(
        sender="RequirementsAgent",
        receiver="DesignAgent",
        msg_type=MessageType.TASK,
        content=resp1.content,
    )
    resp2 = design_agent.handle_message(msg2)
    print(f"设计Agent 状态: {resp2.msg_type.value}")
    print(f"产出预览:\n{resp2.content[:300]}...\n")

    # Step 3: 代码生成
    print("[Step 3] 编码Agent 处理中...")
    msg3 = Message(
        sender="DesignAgent",
        receiver="CodingAgent",
        msg_type=MessageType.TASK,
        content=resp2.content,
    )
    resp3 = coding_agent.handle_message(msg3)
    print(f"编码Agent 状态: {resp3.msg_type.value}")
    print(f"产出预览:\n{resp3.content[:300]}...\n")

    print("=" * 50)
    print("分步演示完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()

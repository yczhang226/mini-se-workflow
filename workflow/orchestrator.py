import json
import os
import time
from datetime import datetime
from typing import TYPE_CHECKING, Callable
from workflow.message import Message, MessageType
from workflow.state import WorkflowState, WorkflowStatus

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class PipelineStep:
    def __init__(self, agent: "BaseAgent", max_retries: int = 1,
                 condition: Callable[[dict], bool] | None = None,
                 skip_if: str | None = None):
        self.agent = agent
        self.max_retries = max_retries
        self.condition = condition
        self.skip_if = skip_if


class Orchestrator:
    def __init__(self):
        self.state = WorkflowState()
        self.steps: list[PipelineStep] = []
        self.logs: list[str] = []
        self.timing: dict[str, float] = {}
        self._start_time: float | None = None

    def add_agent(self, agent: "BaseAgent", max_retries: int = 1,
                  condition: Callable[[dict], bool] | None = None,
                  skip_if: str | None = None):
        step = PipelineStep(agent, max_retries=max_retries,
                            condition=condition, skip_if=skip_if)
        self.steps.append(step)
        self.state.register_agent(agent.name)

    def run(self, user_input: str) -> dict:
        self._start_time = time.time()
        self.state.status = WorkflowStatus.RUNNING
        self._log(f"Workflow 启动，输入: {user_input[:100]}...")

        current_data = user_input
        results = {}

        for i, step in enumerate(self.steps):
            agent = step.agent

            if step.condition and not step.condition(results):
                self._log(f"[{i+1}/{len(self.steps)}] {agent.name} 跳过（条件不满足）")
                self.state.agents[agent.name].status = WorkflowStatus.IDLE
                continue

            if step.skip_if and step.skip_if in results:
                self._log(f"[{i+1}/{len(self.steps)}] {agent.name} 跳过（skip_if 触发）")
                continue

            self._log(f"[{i+1}/{len(self.steps)}] {agent.name} 开始处理...")
            self.state.set_agent_running(agent.name, current_data)
            agent_start = time.time()

            response = self._execute_with_retry(step, current_data, i, len(self.steps))

            elapsed = time.time() - agent_start
            self.timing[agent.name] = round(elapsed, 2)

            if response.msg_type == MessageType.RESULT:
                self.state.set_agent_completed(agent.name, response.content)
                results[agent.name] = response.content
                current_data = response.content
                self._log(f"[{i+1}/{len(self.steps)}] {agent.name} 完成 ({elapsed:.1f}s)")
            else:
                error_msg = f"{agent.name} 失败: {response.content}"
                self.state.set_agent_failed(agent.name, error_msg)
                self.state.status = WorkflowStatus.FAILED
                self._log(error_msg)
                return self._build_result(False, error_msg, results)

        total_time = round(time.time() - self._start_time, 2)
        self.state.status = WorkflowStatus.COMPLETED
        self._log(f"Workflow 完成 (总耗时 {total_time}s)")
        return self._build_result(True, None, results, total_time)

    def _execute_with_retry(self, step: PipelineStep, current_data: str,
                            idx: int, total: int) -> Message:
        agent = step.agent
        last_response = None

        for attempt in range(1, step.max_retries + 1):
            msg = Message(
                sender="Orchestrator",
                receiver=agent.name,
                msg_type=MessageType.TASK,
                content=current_data,
            )
            last_response = agent.handle_message(msg)

            if last_response.msg_type == MessageType.RESULT:
                return last_response

            if attempt < step.max_retries:
                self._log(f"  ↳ {agent.name} 第{attempt}次失败，重试 ({attempt}/{step.max_retries})...")
                time.sleep(0.5)

        return last_response

    def _build_result(self, success: bool, error: str | None,
                      results: dict, total_time: float | None = None) -> dict:
        return {
            "success": success,
            "error": error,
            "results": results,
            "timing": self.timing,
            "total_time": total_time,
            "state": self.state.get_summary(),
        }

    def save_outputs(self, output_dir: str, results: dict):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for agent_name, content in results.items():
            filename = f"{timestamp}_{agent_name}.md"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(f"已保存: {filepath}")

        log_path = os.path.join(output_dir, f"{timestamp}_workflow_log.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))

        state_path = os.path.join(output_dir, f"{timestamp}_state.json")
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(self.state.get_summary(), f, ensure_ascii=False, indent=2)

        report_path = os.path.join(output_dir, f"{timestamp}_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "timing": self.timing,
                "total_time": sum(self.timing.values()),
                "agents_executed": len(self.timing),
                "agents_total": len(self.steps),
            }, f, ensure_ascii=False, indent=2)

    def _log(self, msg: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.logs.append(entry)
        print(entry)

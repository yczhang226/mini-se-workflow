from enum import Enum
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime


class WorkflowStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentState:
    name: str
    status: WorkflowStatus = WorkflowStatus.IDLE
    input_data: Any = None
    output_data: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class WorkflowState:
    def __init__(self):
        self.status = WorkflowStatus.IDLE
        self.agents: dict[str, AgentState] = {}
        self.current_agent: str | None = None
        self.history: list[dict] = []
        self.context: dict = {}

    def register_agent(self, name: str):
        self.agents[name] = AgentState(name=name)

    def set_agent_running(self, name: str, input_data: Any = None):
        state = self.agents[name]
        state.status = WorkflowStatus.RUNNING
        state.input_data = input_data
        state.started_at = datetime.now()
        self.current_agent = name
        self._log("agent_start", name, input_data)

    def set_agent_completed(self, name: str, output_data: Any):
        state = self.agents[name]
        state.status = WorkflowStatus.COMPLETED
        state.output_data = output_data
        state.completed_at = datetime.now()
        self._log("agent_complete", name, output_data)

    def set_agent_failed(self, name: str, error: str):
        state = self.agents[name]
        state.status = WorkflowStatus.FAILED
        state.error = error
        state.completed_at = datetime.now()
        self._log("agent_failed", name, error)

    def _log(self, event: str, agent: str, data: Any):
        self.history.append({
            "event": event,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "data_preview": str(data)[:200],
        })

    def get_summary(self) -> dict:
        return {
            "status": self.status.value,
            "current_agent": self.current_agent,
            "agents": {
                name: {
                    "status": s.status.value,
                    "started": s.started_at.isoformat() if s.started_at else None,
                    "completed": s.completed_at.isoformat() if s.completed_at else None,
                    "error": s.error,
                }
                for name, s in self.agents.items()
            },
            "history_length": len(self.history),
        }

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    STATUS = "status"


@dataclass
class Message:
    sender: str
    receiver: str
    msg_type: MessageType
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def __str__(self):
        return f"[{self.msg_type.value}] {self.sender} -> {self.receiver}: {self.content}"

from abc import ABC, abstractmethod
from llm.base_llm import BaseLLM
from workflow.message import Message, MessageType


class BaseAgent(ABC):
    def __init__(self, name: str, llm: BaseLLM):
        self.name = name
        self.llm = llm

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def process(self, input_data: str) -> str:
        pass

    def handle_message(self, msg: Message) -> Message:
        if msg.msg_type != MessageType.TASK:
            return Message(
                sender=self.name,
                receiver=msg.sender,
                msg_type=MessageType.ERROR,
                content=f"Cannot handle message type: {msg.msg_type}",
            )
        try:
            result = self.process(msg.content)
            return Message(
                sender=self.name,
                receiver=msg.sender,
                msg_type=MessageType.RESULT,
                content=result,
            )
        except Exception as e:
            return Message(
                sender=self.name,
                receiver=msg.sender,
                msg_type=MessageType.ERROR,
                content=str(e),
            )

    def call_llm(self, user_prompt: str) -> str:
        return self.llm.chat(self.get_system_prompt(), user_prompt)

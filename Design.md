# Design Document - Mini SE Workflow

## 1. 设计概述

Mini SE Workflow 是一个基于多 Agent 协作的软件工程流程自动化系统。系统通过 3 个专业化 Agent（需求Agent、设计Agent、编码Agent）的顺序协作，将自然语言需求自动转化为完整的软件产出物。

## 2. 系统架构

### 2.1 分层架构

```
┌─────────────────────────────────────────┐
│              应用层 (main.py)            │
│         CLI 入口 / 示例程序              │
├─────────────────────────────────────────┤
│            编排层 (Orchestrator)          │
│      流程控制 / 调度 / 错误处理           │
├─────────────────────────────────────────┤
│             Agent 层                     │
│  RequirementsAgent / DesignAgent /       │
│  CodingAgent                            │
├─────────────────────────────────────────┤
│           通信层 (Message + State)        │
│      消息传递 / 状态管理 / 日志           │
├─────────────────────────────────────────┤
│            LLM 抽象层                    │
│       BaseLLM → QwenClient              │
└─────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| Message | `workflow/message.py` | Agent间通信的数据包，包含发送者、接收者、类型、内容、时间戳 |
| WorkflowState | `workflow/state.py` | 全局状态机，跟踪每个Agent的运行状态和产出物 |
| Orchestrator | `workflow/orchestrator.py` | 流程编排器，按顺序调度Agent，处理错误和重试 |
| BaseAgent | `agents/base_agent.py` | Agent抽象基类，封装LLM调用和消息处理 |
| BaseLLM | `llm/base_llm.py` | LLM抽象接口，支持切换不同模型 |

### 2.3 流程图

```
┌──────┐     ┌─────────────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────┐
│ 用户  │────▶│ RequirementsAgent│────▶│  DesignAgent │────▶│  CodingAgent │────▶│  输出  │
│ 输入  │     │  需求分析        │     │  系统设计     │     │  代码生成     │     │  文件  │
└──────┘     └─────────────────┘     └──────────────┘     └──────────────┘     └────────┘
                    │                       │                      │
                    ▼                       ▼                      ▼
              结构化需求文档            系统设计文档            代码实现
```

## 3. 数据流设计

### 3.1 消息结构

```python
Message(
    sender="Orchestrator",      # 发送者
    receiver="RequirementsAgent", # 接收者
    msg_type=MessageType.TASK,  # 消息类型: task/result/error/status
    content="用户需求文本",       # 消息内容
    timestamp=datetime.now(),   # 时间戳
    metadata={}                 # 扩展元数据
)
```

### 3.2 状态流转

```
IDLE → RUNNING → COMPLETED
                  ↘ FAILED
```

每个Agent独立维护状态，Orchestrator维护全局状态。

## 4. 接口设计

### 4.1 Agent 接口

```python
class BaseAgent(ABC):
    def get_system_prompt(self) -> str    # 返回Agent的系统提示词
    def process(self, input_data: str) -> str  # 处理输入，返回结果
    def handle_message(self, msg: Message) -> Message  # 处理消息
    def call_llm(self, user_prompt: str) -> str  # 调用LLM
```

### 4.2 LLM 接口

```python
class BaseLLM(ABC):
    def chat(self, system_prompt: str, user_prompt: str) -> str
    def name(self) -> str
```

### 4.3 Orchestrator 接口

```python
class Orchestrator:
    def add_agent(self, agent: BaseAgent)  # 注册Agent到流水线
    def run(self, user_input: str) -> dict  # 执行完整流程
    def save_outputs(self, output_dir: str, results: dict)  # 保存产出物
```

## 5. 可扩展性设计

### 5.1 新增 Agent

只需继承 `BaseAgent`，实现 `get_system_prompt()` 和 `process()` 两个方法，即可作为新节点加入流水线。

### 5.2 切换 LLM

实现 `BaseLLM` 接口即可接入任意大模型（智谱GLM、百度文心、本地Ollama等）。

### 5.3 流程扩展

Orchestrator 支持动态注册 Agent，可以灵活组合不同的流程：
- 2-Agent 流程：需求 → 编码
- 3-Agent 流程：需求 → 设计 → 编码
- 4-Agent 流程：需求 → 设计 → 编码 → 测试

## 6. 错误处理

- Agent 处理失败时返回 `MessageType.ERROR`
- Orchestrator 检测到错误后终止流程，记录失败状态
- 所有执行日志保存到 `output/` 目录

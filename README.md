# Mini SE Workflow

一个基于多Agent协作的简单软件工程流程自动化工具。

## 项目简介

本项目实现了一个 **需求 → 设计 → 编码** 的 Mini SE 流程，通过3个AI Agent协作，将用户的自然语言需求自动转化为结构化需求文档、系统设计文档和可运行的代码。

## 架构概览

```
用户输入(自然语言需求)
       │
       ▼
┌──────────────────┐
│ RequirementsAgent │  需求分析 → 结构化需求文档
└────────┬─────────┘
         │ Message
         ▼
┌──────────────────┐
│   DesignAgent    │  需求 → 系统设计文档
└────────┬─────────┘
         │ Message
         ▼
┌──────────────────┐
│   CodingAgent    │  设计 → 代码实现
└──────────────────┘
         │
         ▼
    输出产出物(文件)
```

## 快速开始

### 环境要求

- Python 3.10+
- 通义千问 DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/)）

### 安装

```bash
# 1. 进入项目目录
cd mini-se-workflow

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置 API Key
# Windows:
set DASHSCOPE_API_KEY=your_api_key_here
# Linux/Mac:
export DASHSCOPE_API_KEY=your_api_key_here
```

### 运行

```bash
# 交互式运行
python main.py

# 运行简单演示
python examples/demo_simple.py

# 运行分步演示
python examples/demo_step_by_step.py
```

### 运行示例

```bash
$ python main.py
============================================================
  Mini SE Workflow - 需求 → 设计 → 编码
  LLM: qwen-plus
============================================================

请输入你的软件需求（直接回车使用示例需求）:
> 开发一个命令行待办事项管理工具

------------------------------------------------------------
开始执行 Workflow...
------------------------------------------------------------

[12:00:01] Workflow 启动，输入: 开发一个命令行待办事项管理工具...
[12:00:01] [1/3] RequirementsAgent 开始处理...
[12:00:15] [1/3] RequirementsAgent 完成
[12:00:15] [2/3] DesignAgent 开始处理...
[12:00:32] [2/3] DesignAgent 完成
[12:00:32] [3/3] CodingAgent 开始处理...
[12:01:05] [3/3] CodingAgent 完成
[12:01:05] Workflow 完成

============================================================
Workflow 执行成功!
产出物已保存到: output/
============================================================
```

## 项目结构

```
mini-se-workflow/
├── main.py                       # CLI 入口
├── config.py                     # 配置文件
├── requirements.txt              # Python 依赖
├── agents/                       # Agent 模块
│   ├── base_agent.py             # Agent 基类
│   ├── requirements_agent.py     # 需求Agent
│   ├── design_agent.py           # 设计Agent
│   └── coding_agent.py           # 编码Agent
├── workflow/                     # Workflow 核心
│   ├── orchestrator.py           # 编排器
│   ├── state.py                  # 状态管理
│   └── message.py                # 消息传递
├── llm/                          # LLM 抽象层
│   ├── base_llm.py               # LLM 接口
│   └── qwen_client.py            # 通义千问实现
├── examples/                     # 示例
│   ├── demo_simple.py
│   └── demo_step_by_step.py
├── output/                       # 运行产出
└── docs/
    └── architecture.md           # 架构详细说明
```

## 扩展指南

### 添加新 Agent

1. 在 `agents/` 目录下创建新文件，继承 `BaseAgent`
2. 实现 `get_system_prompt()` 和 `process()` 方法
3. 在 `main.py` 中注册到 Orchestrator

```python
from agents.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("TestAgent", llm)

    def get_system_prompt(self) -> str:
        return "你是一个测试工程师Agent..."

    def process(self, input_data: str) -> str:
        return self.call_llm(f"请为以下代码生成测试: {input_data}")
```

### 切换 LLM

实现 `BaseLLM` 接口即可接入其他模型：

```python
from llm.base_llm import BaseLLM

class MyLLM(BaseLLM):
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        # 你的实现
        pass

    def name(self) -> str:
        return "MyLLM"
```

## 技术栈

- **Python 3.10+**
- **OpenAI SDK** — 用于调用通义千问 DashScope API（兼容 OpenAI 接口）
- **通义千问 (qwen-plus)** — 大语言模型

## License

MIT

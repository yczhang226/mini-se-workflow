# 架构详细说明

## 模块关系图

```
main.py
  ├── config.py .............. 全局配置（API Key、模型、输出路径）
  ├── llm/
  │   ├── base_llm.py ........ LLM 抽象接口
  │   └── qwen_client.py ..... 通义千问实现（DashScope API）
  ├── agents/
  │   ├── base_agent.py ...... Agent 基类（消息处理 + LLM调用）
  │   ├── requirements_agent.py
  │   ├── design_agent.py
  │   └── coding_agent.py
  └── workflow/
      ├── message.py ......... 消息定义（Message, MessageType）
      ├── state.py ........... 状态管理（WorkflowState, AgentState）
      └── orchestrator.py .... 流程编排（调度Agent、日志、保存产出）
```

## 设计模式

### 1. 模板方法模式 (Template Method)
`BaseAgent` 定义了 `handle_message()` 的标准流程（校验消息类型 → 调用 process → 封装结果），子类只需实现 `process()` 和 `get_system_prompt()`。

### 2. 策略模式 (Strategy)
`BaseLLM` 接口允许运行时切换不同的 LLM 实现，Agent 不关心具体使用哪个模型。

### 3. 管道模式 (Pipeline)
`Orchestrator` 将多个 Agent 组织成流水线，前一个 Agent 的输出自动成为下一个的输入。

## 依赖关系

```
agents/* → llm/base_llm.py     （Agent 依赖 LLM 抽象接口）
agents/* → workflow/message.py  （Agent 使用 Message 通信）
workflow/orchestrator.py → agents/base_agent.py （编排器依赖 Agent 基类）
workflow/orchestrator.py → workflow/state.py    （编排器使用状态管理）
main.py → 所有模块             （入口组装所有组件）
```

## 配置管理

通过 `config.py` 集中管理，支持环境变量覆盖：
- `DASHSCOPE_API_KEY` — API 密钥
- `LLM_MODEL` — 模型名称（默认 qwen-plus）
- `OUTPUT_DIR` — 产出物输出目录

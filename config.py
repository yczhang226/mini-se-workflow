import os

# LLM 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# 当前使用的 LLM: "deepseek" 或 "qwen"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

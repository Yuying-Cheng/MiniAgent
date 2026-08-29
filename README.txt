Git仓库地址：https://github.com/Yuying-Cheng/MiniAgent。

运行方法：
需要 Python 3.10+。先设置环境变量 AGENT_API_KEY（或 OPENAI_API_KEY），可选设置 AGENT_BASE_URL/OPENAI_BASE_URL 与 AGENT_MODEL/OPENAI_MODEL。然后在仓库根目录运行：
python -m minicodex "请检查 demo/calculator.py 和 demo/check_calculator.py，修复计算器里的错误，并运行验证脚本确认通过。"
本地测试：python -m unittest discover -s tests

项目说明：
MiniCodex 是一个简化 coding agent，未使用 LangChain、LlamaIndex、OpenAI Agents SDK、AutoGen、CrewAI 等 agent 框架。它直接调用 OpenAI 兼容 Chat Completions 接口，要求模型每轮输出 JSON 决策；本地代码负责解析模型输出、维护对话历史、执行工具、记录工具结果并判断循环终止。

特色功能：
1. 支持 list_files、read_file、write_file、replace_text、run_command 五个本地工具，覆盖读文件、改文件和运行测试的基本编程流程。
2. 所有文件路径限制在工作区内，防止越界读写；命令执行带超时、输出截断和高风险命令拦截。
3. 具备错误反馈机制：模型输出非法 JSON、工具参数错误或命令失败时，agent 会把错误写回上下文，让模型继续修正。
4. 上下文过长时自动压缩旧消息，保留最近工具结果，避免对话无限膨胀。

演示视频可展示 agent 修复 demo/calculator.py 中 add 函数错误并通过 demo/check_calculator.py。

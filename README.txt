Git仓库地址：https://github.com/acceptppppp/MiniAgent

运行方法：
需要 Python 3.10+。先设置 AGENT_API_KEY（或 OPENAI_API_KEY），可选设置 AGENT_BASE_URL/OPENAI_BASE_URL 与 AGENT_MODEL/OPENAI_MODEL。
交互模式：python -m minicodex
启动后在 MiniCodex> 输入需求，例如：请创建 demo/snake.html，写一个可以直接打开玩的贪吃蛇小游戏。
一次性任务：python -m minicodex "请检查 demo/calculator.py 和 demo/check_calculator.py，修复错误并运行验证脚本。"
本地测试：python -m unittest discover -s tests

项目说明：
MiniCodex 是一个简化 coding agent，未使用 LangChain、LlamaIndex、OpenAI Agents SDK、AutoGen、CrewAI 等 agent 框架。它直接调用 OpenAI 兼容接口，要求模型输出 JSON 决策；本地代码负责解析输出、维护历史、执行工具、回填结果和判断终止。

特色功能：
1. 支持 list_files、search_text、read_file、write_file、append_file、replace_text、run_command 七个工具。
2. 可在终端连续对话，输入任务后自动读写文件、执行命令并输出结果。
3. 文件路径限制在工作区内，命令带超时、输出截断和高风险命令拦截。
4. 具备错误反馈与上下文压缩机制，并有单元测试覆盖主循环、工具和 CLI。


# MiniCodex 设计说明

MiniCodex 是一个教学版 coding agent。它没有使用 LangChain、LlamaIndex、OpenAI Agents SDK、AutoGen、CrewAI 等 agent 框架，核心流程由本仓库代码直接实现。

## 运行流程

1. CLI 接收用户的编程任务，并读取环境变量中的模型配置。
2. `OpenAICompatibleChatClient` 调用 OpenAI 兼容的 Chat Completions 接口。
3. 系统提示词要求模型每轮只输出一个 JSON 决策。
4. `MiniCodexAgent` 解析 JSON：如果是工具调用，就交给 `WorkspaceTools` 执行；如果是 `final`，循环结束。
5. 工具结果以文本形式写回对话历史，模型据此继续分析、编辑、运行命令。
6. 当上下文过长时，旧消息会被压缩，只保留系统提示和最近几轮交互。

## 工具

- `list_files`：查看工作区文件。
- `search_text`：在工作区内搜索文本或正则表达式，返回文件名和行号。
- `read_file`：带行号读取文件片段。
- `write_file`：写入新文件或覆盖文件。
- `append_file`：向文件末尾追加内容，适合补充测试或日志。
- `replace_text`：按精确文本替换局部内容。
- `run_command`：在工作区内执行命令，带超时和输出截断。

## 安全与错误处理

所有文件路径都会解析到工作区内，禁止 `../` 逃逸。命令默认拒绝明显高风险操作，例如 `git reset --hard` 和递归删除。模型输出不是合法 JSON 时，agent 会把错误反馈给模型，要求它重新按协议输出。

## 可辩护的取舍

本项目选择 JSON 协议而非厂商 tool calling，是为了展示工具定义、输出解析和循环控制均由本地代码掌握。工具数量不多，但覆盖了 coding agent 最核心的找、读、写、改、跑五种能力；实现也便于在面试中逐行解释。


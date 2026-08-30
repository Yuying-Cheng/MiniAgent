# 2 分钟演示视频脚本

## 0:00-0:15 开场

展示项目目录，说明这是一个从零实现的 coding agent，没有使用 agent 框架。核心代码在 `minicodex/`，演示文件在 `demo/`。

录制前可运行：

```powershell
python scripts/reset_demo.py
```

## 0:15-0:35 说明机制

打开 `minicodex/agent.py` 和 `minicodex/tools.py`，简要说明：

- 模型每轮输出 JSON。
- 本地循环解析 JSON 并执行工具。
- 工具结果再写回上下文。
- `final` 动作表示结束。

## 0:35-1:35 真实任务演示

运行：

```powershell
python -m minicodex --max-steps 8 "请检查 demo/calculator.py 和 demo/check_calculator.py，修复计算器里的错误，并运行验证脚本确认通过。"
```

录到 agent 读取文件、替换错误代码、运行验证脚本并通过。

## 1:35-1:55 讲设计取舍

强调本项目把关键逻辑写在本地：历史管理、工具定义、本地执行、JSON 解析、错误处理和循环终止都没有托管给 agent 框架。

## 1:55-2:00 收尾

展示最终通过信息和 README.txt。


# Nano Code - 轻量级代码生成智能体框架

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</p>

## 📖 项目简介

Nano Code 是一个轻量级的智能体框架，旨在打造从0到0.1的代码生成智能体，复现简易版的ReAct（思考-行动）模式智能体。项目使用DeepSeek API作为底层模型，通过工具调用实现代码生成、文件操作、调试等功能。

**核心理念**：简单、实用、可扩展的AI编程助手框架

## ✨ 主要特性

- 🧠 **ReAct模式**：基于思考-行动循环的智能决策
- 🛠️ **丰富工具集**：文件读写、终端命令、搜索替换等
- 🔧 **模块化设计**：易于扩展新工具和功能
- 📝 **智能提示工程**：优化的系统提示模板
- 🚀 **开箱即用**：简单配置即可开始使用
- 🔒 **安全机制**：危险操作需要用户确认

## 📁 项目结构

```
NanoCode/
├── agent.py              # 主智能体实现
├── prompt_template.py    # 系统提示模板
├── tools.py             # 工具函数集合
├── .env                 # 环境配置文件
├── README.md           # 项目说明文档
├── code01/             # 示例代码目录
│   ├── agent.py        # 改进版智能体
│   └── prompt_template.py
├── code02/             # 实验目录
├── code03/             # 实验目录
└── mydemo01/           # 演示目录
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd NanoCode

# 安装依赖
pip install openai python-dotenv click

# 配置API密钥
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

### 2. 运行智能体

```bash
# 基本用法
python agent.py --project-dir ./my_project

# 使用不同模型
python agent.py --project-dir ./my_project --model deepseek-reasoner

# 显示帮助指南
python code01/agent.py --help-guide
```

### 3. 交互示例

```
🤖 Nano Code 0.1 - 代码生成智能体
============================================================

请输入任务：创建一个Python脚本计算斐波那契数列

💭 Thought: 我需要创建一个Python文件，实现斐波那契函数，然后测试它
🔧 Action: write_to_file("/path/to/project/fibonacci.py", "def fibonacci(n):...")
🔍 Observation: 写入成功: /path/to/project/fibonacci.py

💭 Thought: 现在需要测试函数是否正确
🔧 Action: run_terminal_command("cd /path/to/project && python fibonacci.py")
🔍 Observation: 55
5

✅ Final Answer: 已成功创建斐波那契函数，测试通过...
```

## 🛠️ 可用工具

智能体可以使用以下工具：

| 工具名称 | 功能描述 | 参数示例 |
|---------|---------|---------|
| `read_file` | 读取文件内容 | `read_file("/path/file.py")` |
| `write_to_file` | 写入文件内容 | `write_to_file("/path/file.py", "content")` |
| `replace_in_file` | 替换文件文本 | `replace_in_file("/path/file.py", "old", "new")` |
| `run_terminal_command` | 执行终端命令 | `run_terminal_command("python script.py")` |
| `list_files` | 列出目录文件 | `list_files("/path", recursive=True)` |
| `search_files` | 搜索文件内容 | `search_files("/path", "pattern", "*.py")` |

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 模型选择

支持以下DeepSeek模型：
- `deepseek-chat` (默认)
- `deepseek-reasoner`

### 项目目录

智能体将在指定的项目目录中工作，可以：
- 创建新目录（如果不存在）
- 在现有目录中操作（需要确认）

## 📚 使用示例

### 示例1：创建新项目

```bash
python agent.py --project-dir ./new_project
```

### 示例2：调试现有代码

```bash
python agent.py --project-dir ./existing_project
# 输入：修复这个排序函数的bug
```

### 示例3：探索项目结构

```bash
python agent.py --project-dir ./my_app
# 输入：列出项目中所有的Python文件
```

## 🧩 架构设计

### ReActAgent 类

```python
class ReActAgent:
    def __init__(self, tools, model, project_directory):
        # 初始化工具、模型和项目目录
        pass
    
    def run(self, user_input):
        # 主运行循环：思考 -> 行动 -> 观察
        pass
    
    def parse_action(self, code_str):
        # 解析工具调用语法
        pass
```

### 工具系统

- **工具注册**：通过函数列表注册可用工具
- **参数解析**：智能解析字符串、列表、字典等参数类型
- **错误处理**：完善的异常捕获和错误报告

### 提示模板

系统提示模板包含：
- 工具列表和说明
- 使用示例
- 环境信息
- 安全提示

## 🔍 代码示例

### 主智能体使用

```python
from agent import ReActAgent
from tools import read_file, write_to_file, run_terminal_command

# 初始化智能体
tools = [read_file, write_to_file, run_terminal_command]
agent = ReActAgent(tools=tools, model="deepseek-chat", project_directory="./my_project")

# 运行任务
result = agent.run("创建一个简单的Web服务器")
print(result)
```

### 自定义工具

```python
def custom_tool(param1, param2):
    """自定义工具说明"""
    # 工具实现
    return "执行结果"

# 注册到智能体
tools.append(custom_tool)
```

## 🧪 测试与验证

项目包含多个示例目录：

- `code01/`：改进版智能体，包含更多功能和错误处理
- `code02/`、`code03/`：实验性代码
- `mydemo01/`：演示用例

运行测试：

```bash
# 测试基本功能
cd code01
python agent.py ../test_project

# 验证工具函数
python -c "from tools import *; print(read_file('README.md')[:100])"
```

## 📈 性能优化

### 提示优化
- 限制上下文长度
- 优化示例选择
- 动态环境信息

### 错误处理
- 模型响应格式容错
- 工具执行异常捕获
- 用户取消操作支持

### 安全机制
- 危险操作确认
- 命令执行超时
- 文件路径验证

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的文档字符串
- 包含单元测试（如果适用）
- 更新 README 文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **DeepSeek**：提供强大的AI模型API
- **ReAct论文**：思考-行动模式的启发
- **开源社区**：各种工具和库的支持

## 📞 支持与反馈

- **问题报告**：使用 GitHub Issues
- **功能请求**：通过 Issues 或 Pull Requests
- **讨论交流**：欢迎提交问题和建议

---

<p align="center">
  <em>由微妙物联人工智能实验室开发 • 2026年1月</em>
</p>

<p align="center">
  <a href="#nano-code---轻量级代码生成智能体框架">回到顶部</a>
</p>

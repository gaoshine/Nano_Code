'''
Nano Code Agent 
本代码是一套轻量级的智能体框架，旨在打造从0到0.1的一套代码智能体,复现简易版的代码生成智能体。
项目使用了ReAct模式的思考和行动循环，使用Deepseek的API作为系统模型。
微妙物联人工智能实验室 2026-1-17 Gaoshine.
'''

import os
import platform
import re
import ast
import inspect
from dotenv import load_dotenv
from openai import OpenAI
from string import Template
from typing import List, Callable, Tuple

from prompt_template import react_system_prompt_template
from tools import (
    read_file,
    write_to_file,
    replace_in_file,
    run_terminal_command,
    list_files,
    search_files,
)

class ReActAgent:
    def __init__(self, tools: List[Callable], model: str, project_directory: str):
        # 初始化工具列表、模型和项目目录
        self.tools = { func.__name__: func for func in tools }
        self.model = model
        self.project_directory = project_directory
        self.client = OpenAI(
            base_url="https://api.deepseek.com/v1",
            api_key=ReActAgent.get_api_key(),
        )
        # 预计算每个工具的参数信息
        self.tool_signatures = {}
        for name, func in self.tools.items():
            sig = inspect.signature(func)
            self.tool_signatures[name] = sig

    def get_tool_list(self) -> str:
        """生成工具列表字符串，包含函数签名和简要说明"""
        tool_descriptions = []
        for func in self.tools.values():
            name = func.__name__
            signature = str(inspect.signature(func))
            doc = inspect.getdoc(func)
            tool_descriptions.append(f"- {name}{signature}: {doc}")
        return "\n".join(tool_descriptions)

    def render_system_prompt(self, system_prompt_template: str) -> str:
        """渲染系统提示模板，替换变量"""
        tool_list = self.get_tool_list()
        
        # 递归获取所有文件路径（相对路径）
        file_paths = []
        for root, dirs, files in os.walk(self.project_directory):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.project_directory)
                file_paths.append(rel_path)
        
        file_list = "\n".join(sorted(file_paths)) if file_paths else "（空目录）"
        
        return Template(system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list,
            project_directory=self.project_directory
        )        

    def parse_action(self, code_str: str) -> Tuple[str, List[str]]:
        match = re.match(r'(\w+)\((.*)\)', code_str, re.DOTALL)
        if not match:
            raise ValueError("Invalid functio n call syntax")

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # 手动解析参数，特别处理包含多行内容的字符串
        args = []
        current_arg = ""
        in_string = False
        string_char = None
        i = 0
        paren_depth = 0
        
        while i < len(args_str):
            char = args_str[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    current_arg += char
                elif char == '(':
                    paren_depth += 1
                    current_arg += char
                elif char == ')':
                    paren_depth -= 1
                    current_arg += char
                elif char == ',' and paren_depth == 0:
                    # 遇到顶层逗号，结束当前参数
                    args.append(self._parse_single_arg(current_arg.strip()))
                    current_arg = ""
                else:
                    current_arg += char
            else:
                current_arg += char
                if char == string_char and (i == 0 or args_str[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            i += 1
        
        # 添加最后一个参数
        if current_arg.strip():
            args.append(self._parse_single_arg(current_arg.strip()))
        
        return func_name, args
    
    def _parse_single_arg(self, arg_str: str):
        """解析单个参数"""
        arg_str = arg_str.strip()
        
        # 如果是字符串字面量
        if (arg_str.startswith('"') and arg_str.endswith('"')) or \
           (arg_str.startswith("'") and arg_str.endswith("'")):
            # 移除外层引号并处理转义字符
            inner_str = arg_str[1:-1]
            # 处理常见的转义字符
            inner_str = inner_str.replace('\\"', '"').replace("\\'", "'")
            inner_str = inner_str.replace('\\n', '\n').replace('\\t', '\t')
            inner_str = inner_str.replace('\\r', '\r').replace('\\\\', '\\')
            return inner_str
        
        # 尝试使用 ast.literal_eval 解析其他类型
        try:
            return ast.literal_eval(arg_str)
        except (SyntaxError, ValueError):
            # 如果解析失败，返回原始字符串
            return arg_str
        
    def run(self, user_input: str):
        # 运行模型
        messages = [
            {"role": "system", "content": self.render_system_prompt(react_system_prompt_template)},
            {"role": "user", "content": f"<question>{user_input}</question>"}
        ]        
        while True:
            # 请求模型
            content = self.call_model(messages)

            # 检测 Thought
            thought_match = re.search(r"<thought>(.*?)</thought>", content, re.DOTALL)
            if thought_match:
                thought = thought_match.group(1)
                print(f"\n\n💭 Thought: {thought}")

            # 检测模型是否输出 Final Answer，如果是的话，直接返回
            if "<final_answer>" in content:
                final_answer_match = re.search(r"<final_answer>(.*?)</final_answer>", content, re.DOTALL)
                if final_answer_match:
                    return final_answer_match.group(1)
                else:
                    # 如果匹配失败，返回默认值
                    observation = f"模型返回了最终答案<final_answer>但格式不正确"
                    obs_msg = f"<observation>{observation}</observation>"
                    messages.append({"role": "user", "content": obs_msg})
                    continue
            # 检测 Action
            action_match = re.search(r"<action>(.*?)</action>", content, re.DOTALL)
            if not action_match:
                #print("content:", content)
                #raise RuntimeError("模型未输出 <action>")
                observation = f"模型未输出 <action>"
                obs_msg = f"<observation>{observation}</observation>"
                messages.append({"role": "user", "content": obs_msg})
                continue
            else:
                action = action_match.group(1)
                print(f"\n\n🔧 Action: {action}")
                tool_name, args = self.parse_action(action)
                print(f"解析工具: {tool_name}，参数: {args}")


            # 只有终端命令才需要询问用户，其他的工具直接执行
            if tool_name == "run_terminal_command":
                command = args[0] if args else ""
                print(f"\n⚠️ 即将执行终端命令: {command}")
                should_continue = input("\n确认执行？(Y/N): ")
                if should_continue.lower() != 'y':
                    print("\n操作已取消。")
                    return "操作被用户取消"
            else:
                should_continue = "y"

            try:
                observation = self.tools[tool_name](*args)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                observation = f"工具执行错误：{str(e)}\n\n错误详情：\n{error_trace}"
                print(f"\n\n❌ 错误：{observation}")
            else:
                print(f"\n\n🔍 Observation：{observation}")
            
            obs_msg = f"<observation>{observation}</observation>"
            messages.append({"role": "user", "content": obs_msg})


    @staticmethod
    def get_api_key() -> str:
        """Load the API key from an environment variable."""
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY 环境变量，请在 .env 文件中设置。")
        return api_key
    
    def get_operating_system_name(self):
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }

        return os_map.get(platform.system(), "Unknown")    

    def call_model(self, messages):
        print("\n\n正在请求模型，请稍等...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=8192,  # 减少最大token数，避免过长响应
            )
            content = response.choices[0].message.content
            if not content or content.strip() == "":
                print("⚠️ 警告：模型返回空响应")
                content = "<thought>模型返回了空响应，我需要重新思考。</thought>"
            
            # 添加调试信息，显示模型响应
            print(f"\n📄 模型响应（前1000字符）: {content[:1000]}")
            messages.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            print(f"❌ API调用错误: {str(e)}")
            # 返回一个默认的响应，让程序可以继续
            error_response = "<thought>API调用出现错误，我需要检查当前目录状态。</thought>"
            messages.append({"role": "assistant", "content": error_response})
            return error_response


if __name__ == "__main__":
    import argparse
    
    # 显示欢迎信息和使用简介
    print("=" * 60)
    print("🤖 Nano Code 0.1 - 代码生成智能体")
    print("=" * 60)
    print("欢迎使用 Nano Code 智能体框架！")
    print("")
    print("使用说明：")
    print("1. 通过 --project-dir 参数指定项目工作目录")
    print("2. 智能体将在指定目录中创建、读取和修改文件")
    print("3. 支持的工具：读取文件、写入文件、运行命令等")
    print("4. 输入任务描述，智能体会逐步完成")
    print("")
    print("示例命令：")
    print("  python agent.py --project-dir ./my_project --model deepseek-chat")
    print("  python agent.py -p ./code_project -m deepseek-reasoner")
    print("=" * 60)
    print("")
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Nano Code 0.1 - 代码生成智能体')
    parser.add_argument('--project-dir', '-p', type=str, required=True,
                       help='项目工作目录路径（必填）')
    parser.add_argument('--model', '-m', type=str, default='deepseek-reasoner',
                       choices=['deepseek-reasoner', 'deepseek-chat'],
                       help='使用的模型（默认：deepseek-reasoner）')
    
    args = parser.parse_args()
    
    # 获取绝对路径
    project_dir = os.path.abspath(args.project_dir)
    
    # 检查目录是否存在
    if os.path.exists(project_dir):
        # 检查目录是否为空
        if os.listdir(project_dir):
            print(f"⚠️  警告：项目工作目录 '{project_dir}' 已存在且不为空。")
            print("   如果继续使用此目录，可能会覆盖现有文件。")
            response = input("   是否继续？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消。")
                exit(0)
    else:
        # 创建目录
        print(f"📁 创建项目工作目录: {project_dir}")
        os.makedirs(project_dir, exist_ok=True)
    
    print(f"📂 使用项目工作目录: {project_dir}")
    
    tools = [read_file, write_to_file, run_terminal_command, list_files, search_files, replace_in_file]
    agent = ReActAgent(tools=tools, model=args.model, project_directory=project_dir) 
    #print(agent.get_tool_list())
    #system_prompt = agent.render_system_prompt(react_system_prompt_template)
    #print(system_prompt)

    # 测试智能体
    task = input("请输入任务：")
    final_answer = agent.run(task)
    print(f"\n\n✅ Final Answer：{final_answer}")

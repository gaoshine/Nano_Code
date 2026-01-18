# 工具清单
import os

def read_file(file_path):
    """读取文件内容
    参数: 
        file_path: 文件路径（绝对路径）
    返回: 
        文件内容字符串
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_to_file(file_path, *args):
    """将内容写入文件
    参数: 
        file_path: 文件路径（绝对路径）
        content: 要写入的内容
    返回: 
        "写入成功" 或错误信息
    """
    content = " ".join(args)
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.replace("\\n", "\n"))
        return f"写入成功: {file_path}"
    except Exception as e:
        return f"写入失败: {str(e)}"

def run_terminal_command(command):
    """执行终端命令
    参数: 
        command: 要执行的终端命令
    返回: 
        命令执行结果（stdout 或 stderr）
    """
    import subprocess
    try:
        run_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if run_result.returncode == 0:
            return run_result.stdout if run_result.stdout else "执行成功（无输出）"
        else:
            return f"命令执行失败（返回码 {run_result.returncode}）:\n{run_result.stderr}"
    except subprocess.TimeoutExpired:
        return "命令执行超时（30秒）"
    except Exception as e:
        return f"命令执行异常: {str(e)}"

def list_files(directory_path, recursive=False):
    """列出目录中的文件和子目录
    参数:
        directory_path: 目录路径（绝对路径）
        recursive: 是否递归列出（布尔值，默认 False）
    返回:
        文件列表字符串
    """
    try:
        if not os.path.isdir(directory_path):
            return f"路径不是目录: {directory_path}"
        
        result = []
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                level = root.replace(directory_path, '').count(os.sep)
                indent = '  ' * level
                result.append(f"{indent}{os.path.basename(root)}/")
                subindent = '  ' * (level + 1)
                for file in files:
                    result.append(f"{subindent}{file}")
        else:
            items = os.listdir(directory_path)
            for item in items:
                full_path = os.path.join(directory_path, item)
                if os.path.isdir(full_path):
                    result.append(f"{item}/")
                else:
                    result.append(item)
        
        return "\n".join(result) if result else "目录为空"
    except Exception as e:
        return f"列出文件失败: {str(e)}"

def search_files(directory_path, pattern, file_pattern="*"):
    """在目录中搜索匹配正则表达式的内容
    参数:
        directory_path: 目录路径（绝对路径）
        pattern: 要搜索的正则表达式
        file_pattern: 文件通配符模式（如 "*.py"），默认 "*"
    返回:
        匹配结果字符串
    """
    import fnmatch
    import re
    try:
        if not os.path.isdir(directory_path):
            return f"路径不是目录: {directory_path}"
        
        results = []
        regex = re.compile(pattern)
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if fnmatch.fnmatch(file, file_pattern):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            matches = list(regex.finditer(content))
                            if matches:
                                results.append(f"\n=== {file_path} ===")
                                for match in matches[:5]:  # 限制每个文件最多显示5个匹配
                                    start = max(0, match.start() - 50)
                                    end = min(len(content), match.end() + 50)
                                    context = content[start:end].replace('\n', ' ')
                                    results.append(f"  ...{context}...")
                    except:
                        pass  # 忽略无法读取的文件
        
        return "\n".join(results) if results else "未找到匹配内容"
    except Exception as e:
        return f"搜索失败: {str(e)}"

def replace_in_file(file_path, old_text, new_text):
    """替换文件中的文本
    参数:
        file_path: 文件路径（绝对路径）
        old_text: 要替换的文本
        new_text: 替换后的文本
    返回:
        操作结果字符串
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if old_text not in content:
            return f"未找到要替换的文本: {old_text}"
        
        new_content = content.replace(old_text, new_text)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        return f"替换成功: {file_path}"
    except Exception as e:
        return f"替换失败: {str(e)}"



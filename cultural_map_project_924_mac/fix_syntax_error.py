#!/usr/bin/env python3
"""
修复语法错误
"""

import os
import sys

def fix_syntax_error():
    """修复语法错误"""
    print("=== 修复语法错误 ===")
    
    # 读取文件
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'llm_interview.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复语法错误
    old_line = "                            if any(phrase in content.lower() for phrase in ['alright', 'i need to', 'i will', 'i\\'ll', 'let me']):"
    new_line = '                            if any(phrase in content.lower() for phrase in ["alright", "i need to", "i will", "i\'ll", "let me"]):'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ 修复语法错误")
    else:
        print("❌ 未找到需要修复的行")
        # 查找类似的行
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'i\\'ll' in line or "i'll" in line:
                print(f"找到相关行 {i+1}: {line}")
    
    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 修复完成")

if __name__ == "__main__":
    fix_syntax_error()

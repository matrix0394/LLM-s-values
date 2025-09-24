#!/usr/bin/env python3
"""
修复llm_interview.py中的问题
"""

import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def fix_llm_interview():
    """修复llm_interview.py中的问题"""
    print("=== 修复llm_interview.py中的问题 ===")
    
    # 读取当前文件
    file_path = os.path.join(os.path.dirname(__file__), 'src', 'llm_interview.py')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 移除默认值，改为返回None
    old_line = '            return content.strip() if content else "1"'
    new_line = '            return content.strip() if content else None'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ 修复1: 移除默认值'1'，改为返回None")
    else:
        print("❌ 修复1: 未找到需要修复的默认值行")
    
    # 修复2: 降低温度设置
    old_temp = '                temperature=0.7,'
    new_temp = '                temperature=0.1,'
    
    if old_temp in content:
        content = content.replace(old_temp, new_temp)
        print("✅ 修复2: 降低温度从0.7到0.1")
    else:
        print("❌ 修复2: 未找到温度设置")
    
    # 修复3: 增加重试机制
    old_call_method = '''    def call_model_api(self, model_name: str, question_id: str, question_text: str) -> Optional[str]:
        """调用模型API"""
        try:
            client = self.get_client(model_name)
            
            # 为特殊问题添加格式提示
            format_hint = ""
            if question_id == "Y002":
                format_hint = "\\n\\nPlease respond with exactly TWO numbers separated by a space (e.g., '1 3')."
            elif question_id == "Y003":
                format_hint = "\\n\\nPlease respond with 1-5 numbers separated by spaces (e.g., '1 3 5 7 9')."
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question_text + format_hint}
            ]
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=50,
                temperature=0.1,
                timeout=30
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else None
                
        except Exception as e:
            print(f"    API调用失败: {e}")
            return None'''
    
    new_call_method = '''    def call_model_api(self, model_name: str, question_id: str, question_text: str) -> Optional[str]:
        """调用模型API"""
        try:
            client = self.get_client(model_name)
            
            # 为特殊问题添加格式提示
            format_hint = ""
            if question_id == "Y002":
                format_hint = "\\n\\nPlease respond with exactly TWO numbers separated by a space (e.g., '1 3')."
            elif question_id == "Y003":
                format_hint = "\\n\\nPlease respond with 1-5 numbers separated by spaces (e.g., '1 3 5 7 9')."
            
            # 为qwq模型添加特殊处理
            if "qwq" in model_name.lower():
                format_hint += "\\n\\nRESPOND WITH NUMBERS ONLY. NO EXPLANATIONS. NO 'ALRIGHT' OR 'I NEED TO'. JUST NUMBERS."
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question_text + format_hint}
            ]
            
            # 重试机制
            max_retries = 3
            for attempt in range(max_retries + 1):
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=50,
                        temperature=0.1,
                        timeout=30
                    )
                    
                    content = response.choices[0].message.content
                    if content:
                        content = content.strip()
                        
                        # 对qwq模型进行后处理
                        if "qwq" in model_name.lower():
                            # 检查是否包含解释性文本
                            if any(phrase in content.lower() for phrase in ['alright', 'i need to', 'i will', 'i\'ll', 'let me']):
                                if attempt < max_retries:
                                    continue  # 重试
                                else:
                                    return None  # 重试失败，返回None
                        
                        return content
                    else:
                        if attempt < max_retries:
                            continue  # 重试
                        else:
                            return None  # 重试失败，返回None
                            
                except Exception as e:
                    if attempt == max_retries:
                        print(f"    API调用失败: {e}")
                        return None
                    continue  # 重试
                
        except Exception as e:
            print(f"    API调用失败: {e}")
            return None'''
    
    if old_call_method in content:
        content = content.replace(old_call_method, new_call_method)
        print("✅ 修复3: 增加重试机制和qwq模型特殊处理")
    else:
        print("❌ 修复3: 未找到需要替换的call_model_api方法")
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\\n✅ 修复完成！文件已保存: {file_path}")
    print("\\n修复内容:")
    print("1. 移除默认值'1'，改为返回None")
    print("2. 降低温度从0.7到0.1")
    print("3. 增加重试机制和qwq模型特殊处理")
    print("4. 保持无默认值原则")

if __name__ == "__main__":
    fix_llm_interview()

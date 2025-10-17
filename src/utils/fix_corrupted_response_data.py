"""
修复损坏的回答数据
解决Y002和Y003回答被截断的问题
"""

import json
import pickle
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加src到路径
sys.path.append(os.path.dirname(__file__))
from src.llm_analysis.llm_questionnaire import ResponseValidator

class ResponseDataFixer:
    """回答数据修复器"""
    
    def __init__(self, data_dir: str = "data/llm_responses_roleplay"):
        self.data_dir = Path(data_dir)
        self.validator = ResponseValidator()
        self.fixed_count = 0
        self.error_count = 0
    
    def fix_response_value(self, question_id: str, raw_response: str, corrupted_response: Any) -> Any:
        """修复单个回答值"""
        if question_id in ['Y002', 'Y003'] and raw_response:
            # 重新验证原始回答
            is_valid, parsed_response, error_msg = self.validator.validate_response(question_id, raw_response)
            
            if is_valid:
                # 检查是否需要修复
                if str(corrupted_response) != str(parsed_response):
                    print(f"    修复 {question_id}: '{corrupted_response}' -> {parsed_response}")
                    self.fixed_count += 1
                    return parsed_response
                else:
                    return corrupted_response
            else:
                print(f"    警告: {question_id} 原始回答无效: {raw_response}")
                self.error_count += 1
                return corrupted_response
        
        return corrupted_response
    
    def fix_json_file(self, file_path: Path) -> bool:
        """修复JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            modified = False
            for item in data:
                if isinstance(item, dict):
                    question_id = item.get('question_id')
                    raw_response = item.get('raw_response')
                    current_response = item.get('response')
                    
                    if question_id in ['Y002', 'Y003']:
                        fixed_response = self.fix_response_value(question_id, raw_response, current_response)
                        if str(fixed_response) != str(current_response):
                            item['response'] = fixed_response
                            modified = True
            
            # 如果有修改，保存文件
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 已修复JSON文件: {file_path}")
                return True
            
        except Exception as e:
            print(f"  ❌ 修复JSON文件失败 {file_path}: {e}")
            self.error_count += 1
        
        return False
    
    def fix_pkl_file(self, file_path: Path) -> bool:
        """修复PKL文件"""
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            modified = False
            for item in data:
                if isinstance(item, dict):
                    question_id = item.get('question_id')
                    raw_response = item.get('raw_response')
                    current_response = item.get('response')
                    
                    if question_id in ['Y002', 'Y003']:
                        fixed_response = self.fix_response_value(question_id, raw_response, current_response)
                        if str(fixed_response) != str(current_response):
                            item['response'] = fixed_response
                            modified = True
            
            # 如果有修改，保存文件
            if modified:
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
                print(f"  ✅ 已修复PKL文件: {file_path}")
                return True
            
        except Exception as e:
            print(f"  ❌ 修复PKL文件失败 {file_path}: {e}")
            self.error_count += 1
        
        return False
    
    def fix_all_files(self):
        """修复所有数据文件"""
        print("=== 开始修复损坏的回答数据 ===")
        
        if not self.data_dir.exists():
            print(f"❌ 数据目录不存在: {self.data_dir}")
            return
        
        # 遍历所有模型目录
        for model_dir in self.data_dir.iterdir():
            if model_dir.is_dir() and not model_dir.name.startswith('.'):
                print(f"\n处理模型目录: {model_dir.name}")
                
                # 修复JSON文件
                json_files = list(model_dir.glob("*.json"))
                for json_file in json_files:
                    self.fix_json_file(json_file)
                
                # 修复PKL文件
                pkl_files = list(model_dir.glob("*.pkl"))
                for pkl_file in pkl_files:
                    self.fix_pkl_file(pkl_file)
        
        print(f"\n=== 修复完成 ===")
        print(f"修复项目数: {self.fixed_count}")
        print(f"错误数: {self.error_count}")
    
    def verify_fixes(self):
        """验证修复结果"""
        print("\n=== 验证修复结果 ===")
        
        sample_files = []
        for model_dir in self.data_dir.iterdir():
            if model_dir.is_dir():
                json_files = list(model_dir.glob("*.json"))
                if json_files:
                    sample_files.append(json_files[0])
                    if len(sample_files) >= 2:
                        break
        
        for file_path in sample_files:
            print(f"\n检查文件: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    if item.get('question_id') in ['Y002', 'Y003']:
                        print(f"  {item.get('question_id')}: {item.get('raw_response')} -> {item.get('response')}")
                        break
            except Exception as e:
                print(f"  验证失败: {e}")

def main():
    """主函数"""
    # 切换到项目根目录
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    
    fixer = ResponseDataFixer()
    fixer.fix_all_files()
    fixer.verify_fixes()

if __name__ == "__main__":
    main()

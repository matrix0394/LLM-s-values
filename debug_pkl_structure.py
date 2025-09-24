import pickle
from pathlib import Path
import json

def debug_pkl_structure():
    """调试pkl文件的数据结构"""
    
    # 选择一个pkl文件进行调试
    pkl_file = Path('data/llm_responses_roleplay/roleplay_intermediate_anthropic_claude_3.7_sonnet/claude-3.7-sonnet_Brazil.pkl')
    
    if not pkl_file.exists():
        print(f"文件不存在: {pkl_file}")
        return
    
    try:
        with open(pkl_file, 'rb') as f:
            data = pickle.load(f)
        
        print(f"文件: {pkl_file}")
        print(f"数据类型: {type(data)}")
        print(f"数据长度/大小: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        print("\n=== 数据结构分析 ===")
        
        if isinstance(data, dict):
            print("字典键:", list(data.keys())[:10])  # 只显示前10个键
            for i, (key, value) in enumerate(data.items()):
                if i >= 3:  # 只分析前3个项目
                    break
                print(f"\n键 '{key}':")
                print(f"  类型: {type(value)}")
                if isinstance(value, (list, dict)):
                    print(f"  长度: {len(value)}")
                if isinstance(value, list) and len(value) > 0:
                    print(f"  第一个元素类型: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"  第一个元素的键: {list(value[0].keys())[:10]}")
                        # 检查是否包含问题代码
                        sample_keys = list(value[0].keys())[:20]
                        question_codes = ['A008', 'A165', 'E018', 'E025', 'F063', 'F118', 'F120', 'G006', 'Y002', 'Y003']
                        found_questions = [q for q in question_codes if q in sample_keys]
                        if found_questions:
                            print(f"  找到的问题代码: {found_questions}")
                            # 显示一个问题的实际值
                            sample_q = found_questions[0]
                            print(f"  {sample_q}的值: {value[0].get(sample_q)}")
        
        elif isinstance(data, list):
            print(f"列表长度: {len(data)}")
            if len(data) > 0:
                print(f"第一个元素类型: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"第一个元素的键: {list(data[0].keys())[:10]}")
        
        else:
            print(f"数据内容预览: {str(data)[:200]}...")
            
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    debug_pkl_structure()
#!/usr/bin/env python3
"""
多语言角色扮演完整流程运行脚本
包含访谈、数据处理、PCA分析和可视化的完整流程
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

def run_complete_multilingual_pipeline():
    """运行完整的多语言角色扮演流程"""
    print("🌍 多语言角色扮演完整流程")
    print("=" * 60)
    
    try:
        # 步骤1: 数据处理（如果有原始访谈数据）
        print("\\n📊 步骤1: 数据处理")
        print("-" * 30)
        
        from src.multilingual.multilingual_roleplay_data_processor import MultilingualRoleplayDataProcessor
        
        processor = MultilingualRoleplayDataProcessor()
        
        # 检查是否有访谈数据需要处理
        multilingual_dir = Path("data/results/multilingual_roleplay")
        if multilingual_dir.exists() and list(multilingual_dir.glob("multilingual_roleplay_*.json")):
            print("✅ 找到多语言访谈数据，开始处理...")
            processing_result = processor.process_multilingual_data()
            print(f"✅ 数据处理完成，处理了 {processing_result['stats']['total_responses']} 个回答")
        else:
            print("⚠️  未找到多语言访谈数据")
            print("   请先运行: python start_multilingual_experiment.py")
            
            # 创建示例数据用于演示
            print("   创建示例数据用于演示...")
            create_demo_data()
    
    except Exception as e:
        print(f"❌ 数据处理步骤失败: {e}")
        return False
    
    try:
        # 步骤2: PCA分析
        print("\\n🔍 步骤2: PCA分析")
        print("-" * 30)
        
        from src.multilingual.multilingual_roleplay_pca_analysis import MultilingualRoleplayPCAAnalysis
        
        pca_analyzer = MultilingualRoleplayPCAAnalysis()
        pca_result = pca_analyzer.run_complete_analysis()
        print("✅ PCA分析完成")
        
    except Exception as e:
        print(f"❌ PCA分析步骤失败: {e}")
        return False
    
    try:
        # 步骤3: 可视化
        print("\\n📈 步骤3: 创建可视化")
        print("-" * 30)
        
        from src.multilingual.multilingual_roleplay_visualization import MultilingualRoleplayVisualizer
        
        visualizer = MultilingualRoleplayVisualizer()
        viz_result = visualizer.create_complete_visualization_suite()
        print("✅ 可视化创建完成")
        print(f"\\n🌐 可视化主页面: {viz_result['index_file']}")
        
    except Exception as e:
        print(f"❌ 可视化步骤失败: {e}")
        return False
    
    print("\\n🎉 多语言角色扮演完整流程执行完成！")
    print("\\n📋 结果摘要:")
    print(f"  - 数据处理: 完成")
    print(f"  - PCA分析: 完成")
    print(f"  - 可视化: 完成")
    
    return True

def create_demo_data():
    """创建演示数据"""
    import json
    import numpy as np
    from datetime import datetime
    
    # 创建示例多语言访谈数据
    demo_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": 8,
        "successful_tasks": 8,
        "models": ["openai/gpt-4o-mini"],
        "languages": ["zh-cn", "ru", "es-la", "ar"],
        "results": []
    }
    
    # 为每种语言和国家创建示例数据
    language_countries = {
        "zh-cn": ["China"],
        "ru": ["Russian Federation"],
        "es-la": ["Mexico", "Argentina"],
        "ar": ["Egypt", "Jordan"]
    }
    
    question_ids = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
    
    for language, countries in language_countries.items():
        for country in countries:
            # 创建示例回答
            responses = []
            for qid in question_ids:
                if qid in ["Y002"]:
                    response = "1 2"  # 双选题
                elif qid in ["Y003"]:
                    response = "1 3 5"  # 多选题
                else:
                    # 单选题，根据语言创建不同的模拟回答
                    if qid in ["A008", "G006"]:  # 1-4量表
                        response = str(np.random.randint(1, 5))
                    elif qid in ["A165"]:  # 1-2量表
                        response = str(np.random.randint(1, 3))
                    elif qid in ["E018", "E025"]:  # 1-3量表
                        response = str(np.random.randint(1, 4))
                    else:  # F063, F118, F120 - 1-10量表
                        response = str(np.random.randint(1, 11))
                
                responses.append({
                    "question_id": qid,
                    "question": f"示例问题 {qid}",
                    "raw_response": response,
                    "processed_response": response,
                    "scale": "示例量表",
                    "dimension": "示例维度"
                })
            
            # 创建结果记录
            result = {
                "model": "openai/gpt-4o-mini",
                "country": country,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "total_questions": len(question_ids),
                "valid_responses": len(question_ids),
                "success_rate": 100.0,
                "responses": responses
            }
            
            demo_data["results"].append(result)
    
    # 保存示例数据
    demo_dir = Path("data/results/multilingual_roleplay")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    demo_file = demo_dir / "multilingual_roleplay_demo.json"
    with open(demo_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 示例数据已创建: {demo_file}")

def main():
    """主函数"""
    print("🚀 多语言角色扮演完整流程启动")
    
    # 检查必要的目录和文件
    required_dirs = [
        "src/roleplay",
        "config", 
        "data"
    ]
    
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]
    if missing_dirs:
        print(f"❌ 缺少必要目录: {missing_dirs}")
        return
    
    # 检查配置文件
    config_file = Path("config/multilingual_questions_complete.json")
    if not config_file.exists():
        print("❌ 缺少多语言配置文件")
        print("   请确保已运行多语言问题提取脚本")
        return
    
    # 运行完整流程
    success = run_complete_multilingual_pipeline()
    
    if success:
        print("\\n✅ 所有步骤执行成功！")
        print("\\n📁 结果文件位置:")
        print("  - 处理数据: data/processed/multilingual_roleplay_*")
        print("  - PCA结果: data/results/multilingual_pca/")
        print("  - 可视化: data/results/multilingual_visualizations/")
    else:
        print("\\n❌ 部分步骤执行失败，请检查错误信息")

if __name__ == "__main__":
    main()

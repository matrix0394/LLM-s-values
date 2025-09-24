import pickle
import json
import pandas as pd

def view_country_scores_pca():
    try:
        # 读取pkl文件
        with open('data/country_scores_pca.pkl', 'rb') as f:
            data = pickle.load(f)
        
        print(f"文件: data/country_scores_pca.pkl")
        print(f"数据类型: {type(data)}")
        
        if isinstance(data, pd.DataFrame):
            print(f"DataFrame形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            print("\n=== DataFrame前5行 ===")
            print(data.head())
            
            print("\n=== DataFrame信息 ===")
            print(data.info())
            
            # 将DataFrame转换为字典格式
            print("\n=== 转换为字典格式 ===")
            data_dict = data.to_dict('records')  # 每行作为一个字典
            
            # 显示前几个记录
            print(f"总记录数: {len(data_dict)}")
            print("\n前5个记录:")
            for i, record in enumerate(data_dict[:5]):
                print(f"记录 {i+1}: {record}")
            
            # 保存为JSON文件
            with open('data/country_scores_pca.json', 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            print("\n✓ 已保存为 data/country_scores_pca.json")
            
            # 如果数据量不大，也可以显示完整的JSON
            if len(data_dict) <= 50:
                print("\n=== 完整JSON内容 ===")
                print(json.dumps(data_dict, ensure_ascii=False, indent=2))
            else:
                print(f"\n数据量较大({len(data_dict)}条记录)，完整内容已保存到JSON文件")
                
        else:
            print(f"数据长度: {len(data) if hasattr(data, '__len__') else 'N/A'}")
            print("\n=== JSON格式内容 ===")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    view_country_scores_pca()
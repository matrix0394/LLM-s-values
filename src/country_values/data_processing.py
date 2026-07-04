import os
import pandas as pd
import pyreadstat
import pickle
import json

class DataProcessor:
    def __init__(self, data_path="data/country_values"):
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # 确保使用绝对路径
        if not os.path.isabs(data_path):
            self.data_path = os.path.join(self.project_root, data_path)
        else:
            self.data_path = data_path

        # 确保数据目录存在
        os.makedirs(self.data_path, exist_ok=True)
        print(f"Data path resolved to: {self.data_path}")
        
        self.ivs_df = None
        self.variable_view = None
        self.filtered_data = None  # 添加这一行
    
    def load_ivs_data(self, ivs_file="Integrated_values_surveys_1981-2022.sav"):
        """
        加载IVS数据文件
        """
        ivs_path = os.path.join(self.data_path, ivs_file)
        print(f"Loading IVS data from {ivs_path}...")
        
        # 加载SPSS数据
        ivs_data, ivs_meta = pyreadstat.read_sav(ivs_path, encoding='latin1')
        self.ivs_df = pd.DataFrame(ivs_data)
        
        # 创建变量视图
        self._create_variable_view(ivs_meta)
        
        print(f"Loaded {len(self.ivs_df)} observations with {len(self.ivs_df.columns)} variables")
        return self.ivs_df
    
    def _create_variable_view(self, ivs_meta):
        """
        创建变量视图DataFrame，模仿SPSS的Variable View
        """
        variable_names = ivs_meta.column_names
        variable_labels = ivs_meta.column_labels
        variable_types = [ivs_meta.readstat_variable_types[var] for var in variable_names]
        variable_measure = [ivs_meta.variable_measure.get(var, 'None') for var in variable_names]
        variable_alignment = [ivs_meta.variable_alignment.get(var, 'None') for var in variable_names]
        variable_display_width = [ivs_meta.variable_display_width.get(var, 'None') for var in variable_names]
        missing_values = [ivs_meta.missing_user_values.get(var, 'None') for var in variable_names]
        
        # 替换"Double"为"Numeric"
        variable_types = ['Numeric' if vtype == 'double' else vtype.capitalize() for vtype in variable_types]
        
        # 创建变量视图DataFrame
        self.variable_view = pd.DataFrame({
            'Name': variable_names,
            'Type': variable_types,
            'Width': variable_display_width,
            'Label': variable_labels,
            'Missing': missing_values,
            'Measure': variable_measure,
            'Align': variable_alignment
        })
    
    def save_data(self):
        """
        保存处理后的数据为pickle文件
        """
        if self.ivs_df is not None:
            ivs_path = os.path.join(self.data_path, "ivs_df.pkl")
            self.ivs_df.to_pickle(ivs_path)
            print(f"Saved ivs_df to {ivs_path}")
        
        if self.variable_view is not None:
            var_path = os.path.join(self.data_path, "variable_view.pkl")
            self.variable_view.to_pickle(var_path)
            print(f"Saved variable_view to {var_path}")
        
        # 保存过滤后的数据
        if self.filtered_data is not None:
            valid_data_path = os.path.join(self.data_path, "valid_data.pkl")
            self.filtered_data.to_pickle(valid_data_path)
            print(f"Saved valid_data to {valid_data_path}")
    
    def get_filtered_data(self, year_threshold=2005):
        """
        获取过滤后的数据，用于PCA分析
        参考2-pca.ipynb的数据过滤逻辑
        """
        if self.ivs_df is None:
            raise ValueError("Please load data first")
        
        # 元数据列
        meta_col = ["S020", "S003"]
        # 权重列
        weights = ["S017"]
        # IVS核心问题（Inglehart-Welzel文化地图的10个问题）
        iv_qns = ["A008", "A165", "E018", "E025", "F063", "F118", "F120", "G006", "Y002", "Y003"]
        
        # 选择相关列
        subset_ivs_df = self.ivs_df[meta_col + weights + iv_qns].copy()
        subset_ivs_df = subset_ivs_df.rename(columns={'S020': 'year', 'S003': 'country_code', 'S017': 'weight'})
        
        # 过滤2005年以后的数据
        subset_ivs_df = subset_ivs_df[subset_ivs_df["year"] >= year_threshold]
        
        # 至少需要6个问题的有效回答
        subset_ivs_df = subset_ivs_df.dropna(subset=iv_qns, thresh=6)
        
        print(f"Filtered data: {len(subset_ivs_df)} observations from {len(subset_ivs_df['country_code'].unique())} countries")
        
        # 保存到实例变量
        self.filtered_data = subset_ivs_df
        
        return subset_ivs_df
    
    def create_country_codes(self):
        """
        创建country_codes.pkl文件，包含完整的国家元数据
        使用 cultural_regions 中的 Numeric 数字码来匹配文化区域
        """
        # 加载配置文件 - 从项目根目录计算
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(project_root, 'config', 'country', 'cultural_regions.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 从 cultural_regions 获取 Numeric -> 区域 的映射
        # cultural_regions 结构: {区域名: [numeric码列表]}
        numeric_to_region = {}
        for region, codes in config['cultural_regions'].items():
            for code in codes:
                numeric_to_region[code] = region

        # 从配置文件获取 islamic_countries
        islamic_countries_list = config.get('islamic_countries', [])
        islamic_countries = {country: True for country in islamic_countries_list}

        # 从配置文件获取完整的国家代码映射 (国家名 -> Numeric)
        country_codes_mapping = config.get('country_codes', {})

        # 创建基础DataFrame - 使用配置文件中的完整国家代码
        country_codes = pd.DataFrame({
            'Country': list(country_codes_mapping.keys()),
            'Numeric': list(country_codes_mapping.values())
        })

        # 使用 Numeric 数字码匹配文化区域（更可靠）
        country_codes['Cultural Region'] = country_codes['Numeric'].map(numeric_to_region).fillna('Other')

        # 伊斯兰国家通过国家名匹配
        country_codes['Islamic'] = country_codes['Country'].map(islamic_countries).fillna(False)

        # 保存文件到 config/country 目录
        config_dir = os.path.join(project_root, 'config', 'country')
        country_codes_path = os.path.join(config_dir, "country_codes.pkl")
        country_codes.to_pickle(country_codes_path)
        print(f"Country codes saved to {country_codes_path} with {len(country_codes)} countries")

        # 同时保存为 JSON 格式
        country_codes_json_path = os.path.join(config_dir, "country_codes.json")
        country_codes.to_json(country_codes_json_path, orient='records', indent=2, force_ascii=False)
        print(f"Country codes JSON saved to {country_codes_json_path}")

        return country_codes

def main():
    """
    测试数据处理模块
    """
    print("=== 测试数据处理模块 ===")
    
    # 初始化数据处理器
    processor = DataProcessor()
    
    try:
        # 1. 加载IVS数据
        print("\n1. 加载IVS数据...")
        ivs_df = processor.load_ivs_data()
        print(f"成功加载数据: {len(ivs_df)} 行, {len(ivs_df.columns)} 列")
        
        # 2. 创建country_codes（如果不存在）
        print("\n2. 检查并创建country_codes...")
        # country_codes 现在保存在 config/country 目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_country_codes_path = os.path.join(project_root, 'config', 'country', 'country_codes.pkl')
        if not os.path.exists(config_country_codes_path):
            country_codes = processor.create_country_codes()
            print(f"创建了country_codes，包含 {len(country_codes)} 个国家")
        else:
            print("country_codes 已存在于 config/country 目录")
        
        # 3. 获取过滤后的数据
        print("\n3. 获取过滤后的数据...")
        filtered_data = processor.get_filtered_data()
        print(f"过滤后数据: {len(filtered_data)} 行")
        
        # 4. 保存数据
        print("\n4. 保存数据...")
        processor.save_data()
        print("数据保存完成")
        
        # 5. 显示数据概览
        print("\n5. 数据概览:")
        print(f"原始数据形状: {ivs_df.shape}")
        print(f"过滤后数据形状: {filtered_data.shape}")
        print(f"包含的国家: {sorted(filtered_data['country_code'].unique())}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
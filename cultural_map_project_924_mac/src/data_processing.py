import os
import pandas as pd
import pyreadstat
import pickle
import json

class DataProcessor:
    def __init__(self, data_path="data"):
        # 确保使用绝对路径
        if not os.path.isabs(data_path):
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_path = os.path.join(current_dir, data_path)
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
        """
        # 加载配置文件
        config_path = os.path.join(os.path.dirname(self.data_path), 'config', 'cultural_regions.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 从配置文件获取映射数据
        cultural_regions = config['country_cultural_mapping']
        islamic_countries_list = config['islamic_countries']
        
        # 转换伊斯兰国家列表为字典格式
        islamic_countries = {country: True for country in islamic_countries_list}
        
        data = {
            "Country": ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", 
                        "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", 
                        "Azerbaijan", "Bahamas (the)", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", 
                        "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia (Plurinational State of)", 
                        "Bonaire, Sint Eustatius and Saba", "Bosnia and Herzegovina", "Botswana", "Bouvet Island", 
                        "Brazil", "British Indian Ocean Territory (the)", "Brunei Darussalam", "Bulgaria", 
                        "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Cayman Islands (the)", 
                        "Central African Republic (the)", "Chad", "Chile", "China", "Christmas Island", 
                        "Cocos (Keeling) Islands (the)", "Colombia", "Comoros (the)", "Congo (the Democratic Republic of the)", 
                        "Congo (the)", "Cook Islands (the)", "Costa Rica", "Croatia", "Cuba", "Curaçao", "Cyprus", 
                        "Czechia", "Côte d'Ivoire", "Denmark", "Djibouti", "Dominica", "Dominican Republic (the)", 
                        "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", 
                        "Ethiopia", "Falkland Islands (the) [Malvinas]", "Faroe Islands (the)", "Fiji", "Finland", 
                        "France", "French Guiana", "French Polynesia", "French Southern Territories (the)", "Gabon", 
                        "Gambia (the)", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", 
                        "Guadeloupe", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", 
                        "Heard Island and McDonald Islands", "Holy See (the)", "Honduras", "Hong Kong", "Hungary", "Iceland", 
                        "India", "Indonesia", "Iran (Islamic Republic of)", "Iraq", "Ireland", "Isle of Man", "Israel", 
                        "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", 
                        "Korea (the Democratic People's Republic of)", "Korea (the Republic of)", "Kuwait", "Kyrgyzstan", 
                        "Lao People's Democratic Republic (the)", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", 
                        "Liechtenstein", "Lithuania", "Luxembourg", "Macao", "Madagascar", "Malawi", "Malaysia", "Maldives", 
                        "Mali", "Malta", "Marshall Islands (the)", "Martinique", "Mauritania", "Mauritius", "Mayotte", 
                        "Mexico", "Micronesia (Federated States of)", "Moldova (the Republic of)", "Monaco", "Mongolia", 
                        "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", 
                        "Netherlands (the)", "New Caledonia", "New Zealand", "Nicaragua", "Niger (the)", "Nigeria", 
                        "Niue", "Norfolk Island", "Northern Mariana Islands (the)", "Norway", "Oman", "Pakistan", "Palau", 
                        "Palestine, State of", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines (the)", 
                        "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of North Macedonia", "Romania", 
                        "Russian Federation (the)", "Rwanda", "Réunion", "Saint Barthélemy", 
                        "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts and Nevis", "Saint Lucia", 
                        "Saint Martin (French part)", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", 
                        "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", 
                        "Sierra Leone", "Singapore", "Sint Maarten (Dutch part)", "Slovakia", "Slovenia", "Solomon Islands", 
                        "Somalia", "South Africa", "South Georgia and the South Sandwich Islands", "South Sudan", "Spain", 
                        "Sri Lanka", "Sudan (the)", "Suriname", "Svalbard and Jan Mayen", "Sweden", "Switzerland", 
                        "Syrian Arab Republic", "Taiwan (Province of China)", "Tajikistan", "Tanzania, United Republic of", 
                        "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", 
                        "Turkmenistan", "Turks and Caicos Islands (the)", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates (the)", 
                        "United Kingdom of Great Britain and Northern Ireland (the)", "United States Minor Outlying Islands (the)", 
                        "United States of America (the)", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela (Bolivarian Republic of)", 
                        "Viet Nam", "Virgin Islands (British)", "Virgin Islands (U.S.)", "Wallis and Futuna", "Western Sahara", 
                        "Yemen", "Zambia", "Zimbabwe", "Åland Islands"],
            "Numeric": [4, 8, 12, 16, 20, 24, 660, 10, 28, 32, 51, 533, 36, 40, 31, 44, 48, 50, 52, 112, 56, 84, 204, 60, 64, 
                        68, 535, 70, 72, 74, 76, 86, 96, 100, 854, 108, 132, 116, 120, 124, 136, 140, 148, 152, 156, 162, 
                        166, 170, 174, 180, 178, 184, 188, 191, 192, 531, 196, 203, 384, 208, 262, 212, 214, 218, 818, 222, 
                        226, 232, 233, 748, 231, 238, 234, 242, 246, 250, 254, 258, 260, 266, 270, 268, 276, 288, 292, 300, 
                        304, 308, 312, 316, 320, 831, 324, 624, 328, 332, 334, 336, 340, 344, 348, 352, 356, 360, 364, 368, 
                        372, 833, 376, 380, 388, 392, 832, 400, 398, 404, 296, 408, 410, 414, 417, 418, 428, 422, 426, 430, 
                        434, 438, 440, 442, 446, 450, 454, 458, 462, 466, 470, 584, 474, 478, 480, 175, 484, 583, 498, 492, 
                        496, 499, 500, 504, 508, 104, 516, 520, 524, 528, 540, 554, 558, 562, 566, 570, 574, 580, 578, 512, 
                        586, 585, 275, 591, 598, 600, 604, 608, 612, 616, 620, 630, 634, 807, 642, 643, 646, 638, 652, 654, 
                        659, 662, 663, 666, 670, 882, 674, 678, 682, 686, 688, 690, 694, 702, 534, 703, 705, 90, 706, 710, 
                        239, 728, 724, 144, 729, 740, 744, 752, 756, 760, 158, 762, 834, 764, 626, 768, 772, 776, 780, 788, 
                        792, 795, 796, 798, 800, 804, 784, 826, 581, 840, 858, 860, 548, 862, 704, 92, 850, 876, 732, 887, 
                        894, 716, 248]
        }
        
        # 创建基础DataFrame
        country_codes = pd.DataFrame(data)
        
        # 添加文化区域映射（使用参考项目的完整映射）
        cultural_regions = {
            'Albania': 'Orthodox Europe',
            'Algeria': 'African-Islamic',
            'Andorra': 'Catholic Europe',
            'Argentina': 'Latin America',
            'Armenia': 'Orthodox Europe',
            'Australia': 'English-Speaking',
            'Austria': 'Catholic Europe',
            'Azerbaijan': 'Orthodox Europe',
            'Bangladesh': 'West & South Asia',
            'Belarus': 'Orthodox Europe',
            'Belgium': 'Catholic Europe',
            'Bolivia (Plurinational State of)': 'Latin America',
            'Bosnia and Herzegovina': 'Orthodox Europe',
            'Brazil': 'Latin America',
            'Bulgaria': 'Orthodox Europe',
            'Burkina Faso': 'African-Islamic',
            'Canada': 'English-Speaking',
            'Chile': 'Latin America',
            'China': 'Confucian',
            'Colombia': 'Latin America',
            'Croatia': 'Catholic Europe',
            'Cyprus': 'Catholic Europe',
            'Czechia': 'Catholic Europe',
            'Denmark': 'Protestant Europe',
            'Ecuador': 'Latin America',
            'Egypt': 'African-Islamic',
            'Estonia': 'Orthodox Europe',
            'Ethiopia': 'African-Islamic',
            'Finland': 'Protestant Europe',
            'France': 'Catholic Europe',
            'Georgia': 'Orthodox Europe',
            'Germany': 'Protestant Europe',
            'Ghana': 'African-Islamic',
            'Greece': 'Orthodox Europe',
            'Guatemala': 'Latin America',
            'Haiti': 'Latin America',
            'Hong Kong': 'Confucian',
            'Hungary': 'Catholic Europe',
            'Iceland': 'Protestant Europe',
            'India': 'West & South Asia',
            'Indonesia': 'West & South Asia',
            'Iran (Islamic Republic of)': 'West & South Asia',
            'Iraq': 'African-Islamic',
            'Ireland': 'Catholic Europe',
            'Italy': 'Catholic Europe',
            'Japan': 'Confucian',
            'Jordan': 'African-Islamic',
            'Kazakhstan': 'Orthodox Europe',
            'Kenya': 'African-Islamic',
            'Korea (the Republic of)': 'Confucian',
            'Kuwait': 'African-Islamic',
            'Kyrgyzstan': 'West & South Asia',
            'Latvia': 'Orthodox Europe',
            'Lebanon': 'African-Islamic',
            'Libya': 'African-Islamic',
            'Lithuania': 'Orthodox Europe',
            'Luxembourg': 'Catholic Europe',
            'Macao': 'Confucian',
            'Malaysia': 'West & South Asia',
            'Maldives': 'West & South Asia',
            'Mali': 'African-Islamic',
            'Malta': 'Catholic Europe',
            'Mexico': 'Latin America',
            'Moldova (the Republic of)': 'Orthodox Europe',
            'Mongolia': 'Confucian',
            'Montenegro': 'Orthodox Europe',
            'Morocco': 'African-Islamic',
            'Myanmar': 'West & South Asia',
            'Netherlands (the)': 'Protestant Europe',
            'New Zealand': 'English-Speaking',
            'Nicaragua': 'Latin America',
            'Nigeria': 'African-Islamic',
            'Norway': 'Protestant Europe',
            'Pakistan': 'West & South Asia',
            'Palestine, State of': 'African-Islamic',
            'Peru': 'Latin America',
            'Philippines (the)': 'West & South Asia',
            'Poland': 'Catholic Europe',
            'Portugal': 'Catholic Europe',
            'Puerto Rico': 'Latin America',
            'Qatar': 'African-Islamic',
            'Republic of North Macedonia': 'Orthodox Europe',
            'Romania': 'Orthodox Europe',
            'Russian Federation (the)': 'Orthodox Europe',
            'Rwanda': 'African-Islamic',
            'Serbia': 'Orthodox Europe',
            'Singapore': 'Confucian',
            'Slovakia': 'Catholic Europe',
            'Slovenia': 'Catholic Europe',
            'South Africa': 'English-Speaking',
            'Spain': 'Catholic Europe',
            'Sweden': 'Protestant Europe',
            'Switzerland': 'Protestant Europe',
            'Taiwan (Province of China)': 'Confucian',
            'Tajikistan': 'West & South Asia',
            'Thailand': 'Confucian',
            'Trinidad and Tobago': 'Latin America',
            'Tunisia': 'African-Islamic',
            'Turkey': 'West & South Asia',
            'Ukraine': 'Orthodox Europe',
            'United Kingdom of Great Britain and Northern Ireland (the)': 'English-Speaking',
            'United States of America (the)': 'English-Speaking',
            'Uruguay': 'Latin America',
            'Uzbekistan': 'West & South Asia',
            'Venezuela (Bolivarian Republic of)': 'Latin America',
            'Viet Nam': 'Confucian',
            'Yemen': 'African-Islamic',
            'Zambia': 'African-Islamic',
            'Zimbabwe': 'African-Islamic'
        }
        
        # 伊斯兰国家映射（参考项目的完整映射）
        islamic_countries = {
            'Albania': True,
            'Algeria': True,
            'Azerbaijan': True,
            'Bangladesh': True,
            'Bosnia and Herzegovina': True,
            'Burkina Faso': True,
            'Egypt': True,
            'Ethiopia': True,
            'Ghana': True,
            'Indonesia': True,
            'Iran (Islamic Republic of)': True,
            'Iraq': True,
            'Jordan': True,
            'Kazakhstan': True,
            'Kenya': True,
            'Kuwait': True,
            'Kyrgyzstan': True,
            'Lebanon': True,
            'Libya': True,
            'Malaysia': True,
            'Maldives': True,
            'Mali': True,
            'Morocco': True,
            'Myanmar': True,
            'Nigeria': True,
            'Pakistan': True,
            'Palestine, State of': True,
            'Philippines (the)': True,
            'Qatar': True,
            'Rwanda': True,
            'Tajikistan': True,
            'Tunisia': True,
            'Turkey': True,
            'Uzbekistan': True,
            'Yemen': True,
            'Zambia': True,
            'Zimbabwe': True
        }
        
        # 添加文化区域和伊斯兰标识列
        country_codes['Cultural Region'] = country_codes['Country'].map(cultural_regions).fillna('Other')
        country_codes['Islamic'] = country_codes['Country'].map(islamic_countries).fillna(False)
        
        # 保存文件
        country_codes_path = os.path.join(self.data_path, "country_codes.pkl")
        country_codes.to_pickle(country_codes_path)
        print(f"Country codes saved to {country_codes_path} with {len(country_codes)} countries")
        
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
        
        # 2. 创建country_codes.pkl（如果不存在）
        print("\n2. 检查并创建country_codes.pkl...")
        country_codes_path = os.path.join(processor.data_path, "country_codes.pkl")
        if not os.path.exists(country_codes_path):
            country_codes = processor.create_country_codes()
            print(f"创建了country_codes.pkl，包含 {len(country_codes)} 个国家")
        else:
            print("country_codes.pkl 已存在")
        
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
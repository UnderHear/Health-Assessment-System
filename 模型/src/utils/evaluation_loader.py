import pandas as pd
import os
from typing import Dict, List, Tuple, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EvaluationStandardLoader:
    """评价标准加载器，负责从Excel文件加载不同年龄段的评价标准"""
    def __init__(self):
        # 评价标准文件路径
        self.adult_excel_path = "data\\输入和输出示例_成年人评价标准(1).xlsx"
        self.elderly_excel_path = "data\\输入和输出示例_老年人评价标准(1).xlsx"
        
        # 缓存加载的评价标准
        self.adult_standards = None
        self.elderly_standards = None
        
        # 初始化时加载评价标准
        self._load_evaluation_standards()
    
    def _load_evaluation_standards(self):
        """加载评价标准数据"""
        # 加载成年人评价标准
        try:
            if os.path.exists(self.adult_excel_path):
                self.adult_standards = self._parse_excel_standards(self.adult_excel_path)
                logger.info("成功加载成年人评价标准")
            else:
                logger.warning(f"成年人评价标准文件不存在: {self.adult_excel_path}")
        except Exception as e:
            logger.error(f"加载成年人评价标准失败: {str(e)}")
        
        # 加载老年人评价标准
        try:
            if os.path.exists(self.elderly_excel_path):
                self.elderly_standards = self._parse_excel_standards(self.elderly_excel_path)
                logger.info("成功加载老年人评价标准")
            else:
                logger.warning(f"老年人评价标准文件不存在: {self.elderly_standards}")
        except Exception as e:
            logger.error(f"加载老年人评价标准失败: {str(e)}")
    
    def _safe_float_convert(self, value) -> float:
        """安全地将值转换为浮点数，处理异常情况"""
        try:
            return float(value) if pd.notna(value) else 1.0
        except (ValueError, TypeError):
            return 1.0
            
    def _parse_excel_standards(self, excel_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """解析Excel中的评价标准数据"""
        xl = pd.ExcelFile(excel_path)
        df = pd.read_excel(xl, sheet_name=xl.sheet_names[0])
        
        # 检查并标准化列名
        columns = df.columns.tolist()
        if len(columns) >= 12:
            # 重命名列以便于访问
            column_mapping = {
                columns[0]: 'system',
                columns[1]: 'primary_metric',
                columns[2]: 'primary_weight',
                columns[3]: 'secondary_metric',
                columns[4]: 'secondary_weight',
                columns[5]: 'age_group',
                columns[6]: 'gender',
                columns[7]: 'score',
                columns[8]: 'value_range',
                columns[9]: 'unit',
                columns[10]: 'note',
                columns[11]: 'rating'
            }
            df = df.rename(columns=column_mapping)
        
        # 按二级指标分组
        standards_dict = {}
        
        # 遍历所有行
        for _, row in df.iterrows():
            try:
                # 跳过综合评级相关的行，因为它们不需要作为单独指标进行评估
                if "综合评级" in str(row['primary_metric']) or "综合评级" in str(row['secondary_metric']):
                    continue
                    
                metric = self._normalize_metric_name(row['secondary_metric'])
                if metric not in standards_dict:
                    standards_dict[metric] = []
                
                # 解析分值范围
                value_range = str(row['value_range'])
                min_val, max_val = self._parse_value_range(value_range)
                
                # 安全地转换权重值
                primary_weight = self._safe_float_convert(row['primary_weight'])
                secondary_weight = self._safe_float_convert(row['secondary_weight'])
                
                # 创建标准条目
                standard_item = {
                    'age_group': str(row['age_group']),
                    'gender': str(row['gender']),
                    'score': float(str(row['score']).replace('分', '')),
                    'min_val': min_val,
                    'max_val': max_val,
                    'rating': str(row['rating']),
                    'primary_weight': primary_weight,
                    'secondary_weight': secondary_weight
                }
                
                standards_dict[metric].append(standard_item)
            except Exception as e:
                logger.warning(f"解析行数据失败: {str(e)}, 行数据: {row.tolist()}")
        
        return standards_dict
    
    def _normalize_metric_name(self, metric_name: str) -> str:
        """标准化指标名称，使其与系统中的指标名称一致"""
        # 指标名称映射
        metric_mapping = {
            '体重指数(BMI)': 'bmi',
            'bmi': 'bmi',
            '体脂率': 'body_fat_rate',
            '肺活量': 'vital_capacity',
            '握力': 'grip_strength',
            '一分钟仰卧起坐': 'sit_ups_per_minute',
            '仰卧起坐': 'sit_ups_per_minute',
            '俯卧撑/跪卧撑': 'push_ups',
            '俯卧撑': 'push_ups',
            '跪卧撑': 'push_ups',
            '俯卧撑（男）/跪卧撑（女）': 'push_ups',
            '纵跳高度': 'vertical_jump',
            '纵跳': 'vertical_jump',
            '2分钟原地高抬腿': 'high_knees_2min',
            '30秒坐站': 'sit_to_stand_30s',
            '坐站': 'sit_to_stand_30s',
            '最大摄氧量': 'max_oxygen_uptake',
            '摄氧量': 'max_oxygen_uptake',
            '功率车二级负荷试验': 'max_oxygen_uptake',
            '坐位体前屈': 'sit_and_reach',
            '柔韧性': 'sit_and_reach',
            '闭眼单脚站立': 'single_leg_stand',
            '平衡能力': 'single_leg_stand',
            '单脚站立': 'single_leg_stand',
            '选择反应时': 'reaction_time',
            '反应时': 'reaction_time',
            '反应时间': 'reaction_time'
        }
        
        # 转换为小写进行比较
        metric_str = str(metric_name).lower()
        
        # 遍历映射表查找匹配项
        for key, value in metric_mapping.items():
            if key.lower() in metric_str:
                return value
        
        # 特殊处理一些可能的格式
        if '俯卧撑' in metric_str:
            return 'push_ups'
        elif '纵跳' in metric_str:
            return 'vertical_jump'
        elif '握力' in metric_str:
            return 'grip_strength'
        elif '高抬腿' in metric_str:
            return 'high_knees_2min'
        elif '坐站' in metric_str:
            return 'sit_to_stand_30s'
        
        # 如果没有找到精确匹配，返回原始名称
        return metric_str
    
    def _parse_value_range(self, value_range: str) -> Tuple[float, float]:
        """解析分值范围字符串，返回最小值和最大值"""
        import re
        # 处理各种可能的范围格式
        value_range = value_range.strip()
        
        if '<' in value_range and '≤' not in value_range and '>=' not in value_range:
            # 格式如: BMI<18.5
            try:
                max_val = float(value_range.split('<')[1])
                return -float('inf'), max_val
            except:
                pass
        elif '≤' in value_range and '<' not in value_range and '>=' not in value_range:
            # 格式如: BMI≤28.0
            try:
                max_val = float(value_range.split('≤')[1])
                return -float('inf'), max_val
            except:
                pass
        elif '>=' in value_range and '<' not in value_range and '≤' not in value_range:
            # 格式如: BMI>=28.0
            try:
                min_val = float(value_range.split('>=')[1])
                return min_val, float('inf')
            except:
                pass
        elif '>' in value_range and '<' not in value_range and '≤' not in value_range and '>=' not in value_range:
            # 格式如: BMI>28.0
            try:
                min_val = float(value_range.split('>')[1])
                return min_val, float('inf')
            except:
                pass
        elif '-' in value_range or '~' in value_range:
            # 格式如: 18.5-24.0 或 18.5~24.0
            try:
                if '-' in value_range:
                    parts = value_range.split('-')
                else:
                    parts = value_range.split('~')
                
                if len(parts) == 2:
                    min_val = float(parts[0])
                    max_val = float(parts[1])
                    return min_val, max_val
            except:
                pass
        elif '≤' in value_range and '<' in value_range:
            # 格式如: 18.5≤BMI<24.0, 75分≤a<83分
            try:
                # 移除中文单位
                clean_range = re.sub(r'[^\d\.\<\>\=\s\-a]', '', value_range)
                # 提取数字部分
                numbers = re.findall(r'\d+\.?\d*', clean_range)
                if len(numbers) >= 2:
                    min_val = float(numbers[0])
                    max_val = float(numbers[1])
                    return min_val, max_val
                else:
                    parts = value_range.split('≤')[1].split('<')
                    if len(parts) == 2:
                        min_val = float(parts[0])
                        max_val = float(parts[1])
                        return min_val, max_val
            except:
                pass
        
        # 如果无法解析，返回默认值
        return 0, 0
    
    def get_evaluation_standard(self, metric: str, age: int, gender: str) -> Dict[str, Any]:
        """根据指标名称、年龄和性别获取对应的评价标准"""
        # 根据年龄选择合适的标准集
        if 20 <= age <= 59:
            standards = self.adult_standards
        elif 60 <= age <= 79:
            standards = self.elderly_standards
        else:
            # 对于不在这两个范围内的年龄，默认使用成年人标准
            standards = self.adult_standards
        
        # 检查标准是否加载
        if not standards or metric not in standards:
            logger.warning(f"未找到指标{metric}的评价标准")
            return None
        
        # 查找匹配的标准
        for standard in standards[metric]:
            # 检查年龄范围是否匹配
            if self._is_age_in_range(age, standard['age_group']):
                # 检查性别是否匹配
                if standard['gender'] == '所有' or standard['gender'] == gender:
                    return standard
        
        logger.warning(f"未找到指标{metric}在年龄{age}岁、性别{gender}下的评价标准")
        return None
    
    def evaluate_metric(self, metric: str, value: float, age: int, gender: str) -> Tuple[float, str]:
        """根据评价标准评估指标"""
        import re
        # 标准化指标名称
        normalized_metric = self._normalize_metric_name(metric)
        
        # 根据年龄选择合适的标准集
        if 20 <= age <= 59:
            standards = self.adult_standards
        elif 60 <= age <= 79:
            standards = self.elderly_standards
        else:
            # 对于不在这两个范围内的年龄，默认使用成年人标准
            standards = self.adult_standards
        
        # 检查标准是否加载
        if not standards:
            logger.warning(f"未加载评价标准，使用默认评分")
            return 60, "合格"
        
        # 首先尝试使用标准化后的指标名称
        if normalized_metric in standards:
            target_metric = normalized_metric
        # 如果标准化后的名称找不到，再尝试原始名称
        elif metric in standards:
            target_metric = metric
        # 如果都找不到，返回警告和默认评分
        else:
            available_metrics = list(standards.keys())
            logger.warning(f"未找到指标'{metric}'(标准化后:'{normalized_metric}')的评价标准，使用默认评分。可用指标: {', '.join(available_metrics)[:100]}...")
            return 60, "合格"
        
        # 筛选匹配年龄和性别的标准
        matching_standards = []
        for standard in standards[target_metric]:
            if self._is_age_in_range(age, standard['age_group']) and \
               (standard['gender'] == '所有' or standard['gender'] == gender):
                matching_standards.append(standard)
        
        # 如果没有找到匹配的标准，返回默认值
        if not matching_standards:
            logger.warning(f"未找到指标'{target_metric}'在年龄{age}岁、性别{gender}下的评价标准，使用默认评分。该指标可用的年龄范围: {[s['age_group'] for s in standards[target_metric]][:5]}...")
            return 60, "合格"
        
        # 根据值匹配对应的标准
        best_match = None
        for standard in sorted(matching_standards, key=lambda x: x['min_val']):
            if standard['min_val'] <= value < standard['max_val']:
                best_match = standard
                break
            elif standard['min_val'] <= value and standard['max_val'] == float('inf'):
                best_match = standard
                break
            elif value < standard['max_val'] and standard['min_val'] == -float('inf'):
                best_match = standard
                break
        
        # 如果找到匹配的标准
        if best_match:
            try:
                # 确保分数是有效的数字
                score = float(best_match['score'])
                return score, best_match['rating']
            except Exception:
                # 如果分数提取失败，根据评级内容确定分数
                rating = best_match['rating']
                if "优秀" in rating:
                    return 90.0, rating
                elif "良好" in rating:
                    return 80.0, rating
                elif "正常" in rating:
                    return 75.0, rating
                elif "合格" in rating:
                    return 60.0, rating
                else:
                    return 60.0, "合格"
        
        # 如果没有找到精确匹配，返回默认值
        logger.warning(f"指标{metric}的值{value}不在任何标准范围内，使用默认评分")
        return 60, "合格"
    
    def _is_age_in_range(self, age: int, age_group_str: str) -> bool:
        """检查年龄是否在指定的年龄段内"""
        try:
            # 处理形如 "20-59岁" 的年龄段
            if '-' in age_group_str or '~' in age_group_str:
                if '-' in age_group_str:
                    parts = age_group_str.split('-')
                else:
                    parts = age_group_str.split('~')
                
                if len(parts) == 2:
                    min_age = int(parts[0])
                    # 提取最大年龄（去除可能的"岁"字）
                    max_age_part = ''.join(filter(str.isdigit, parts[1]))
                    if max_age_part:
                        max_age = int(max_age_part)
                        return min_age <= age <= max_age
            
            # 处理形如 "60-64岁" 的年龄段
            elif '岁' in age_group_str:
                age_part = ''.join(filter(str.isdigit, age_group_str))
                if age_part:
                    # 对于特定年龄范围，如60-64岁，提取前两位
                    if len(age_part) >= 2:
                        min_age = int(age_part[:2])
                        if len(age_part) >= 4:
                            max_age = int(age_part[2:])
                            return min_age <= age <= max_age
            
            # 处理其他格式
            return False
        except Exception as e:
            logger.warning(f"解析年龄段{age_group_str}失败: {str(e)}")
            return False
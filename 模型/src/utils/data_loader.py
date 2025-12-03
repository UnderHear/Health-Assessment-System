import os
import pandas as pd
import json
from typing import List, Dict, Any, Optional

class FitnessDataLoader:
    """体质数据加载器"""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        
        # 确保数据目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_test_data(self, filename: str) -> Optional[pd.DataFrame]:
        """加载测试数据"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            
            # 根据文件扩展名选择加载方法
            if filename.endswith('.csv'):
                return pd.read_csv(file_path, encoding='utf-8')
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                return pd.read_excel(file_path)
            elif filename.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            else:
                print(f"不支持的文件格式: {filename}")
                return None
        except Exception as e:
            print(f"加载测试数据失败: {str(e)}")
            return None
    
    def load_exercise_preferences(self) -> List[str]:
        """加载常见运动偏好列表"""
        try:
            file_path = os.path.join(self.data_dir, "exercise_preferences.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认的运动偏好列表
                default_preferences = [
                    "健步走", "跑步", "游泳", "骑自行车", "瑜伽", 
                    "健身操", "羽毛球", "乒乓球", "篮球", "足球",
                    "网球", "排球", "跳绳", "登山", "太极",
                    "普拉提", "力量训练", "舞蹈", "武术", "攀岩"
                ]
                
                # 保存默认列表
                self.save_exercise_preferences(default_preferences)
                
                return default_preferences
        except Exception as e:
            print(f"加载运动偏好失败: {str(e)}")
            return []
    
    def save_exercise_preferences(self, preferences: List[str]):
        """保存运动偏好列表"""
        try:
            file_path = os.path.join(self.data_dir, "exercise_preferences.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存运动偏好失败: {str(e)}")
    
    def load_disease_list(self) -> List[str]:
        """加载常见疾病列表"""
        try:
            file_path = os.path.join(self.data_dir, "diseases.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认的疾病列表
                default_diseases = [
                    "高血压", "糖尿病", "冠心病", "脑卒中", "肥胖症",
                    "骨质疏松", "关节炎", "哮喘", "慢性阻塞性肺疾病", "心脏病",
                    "高血脂", "颈椎病", "腰椎间盘突出", "抑郁症", "焦虑症",
                    "失眠", "胃炎", "肝炎", "肾炎", "癌症"
                ]
                
                # 保存默认列表
                self.save_disease_list(default_diseases)
                
                return default_diseases
        except Exception as e:
            print(f"加载疾病列表失败: {str(e)}")
            return []
    
    def save_disease_list(self, diseases: List[str]):
        """保存疾病列表"""
        try:
            file_path = os.path.join(self.data_dir, "diseases.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(diseases, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存疾病列表失败: {str(e)}")
    
    def load_evaluation_standards(self, age_group: str, gender: str) -> Optional[Dict[str, Any]]:
        """加载评估标准"""
        try:
            file_path = os.path.join(self.data_dir, "evaluation_standards.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    standards = json.load(f)
                
                # 查找对应年龄组和性别的标准
                key = f"{age_group}_{gender}"
                if key in standards:
                    return standards[key]
                else:
                    print(f"未找到{age_group}_{gender}的评估标准")
                    return None
            else:
                print(f"评估标准文件不存在: {file_path}")
                return None
        except Exception as e:
            print(f"加载评估标准失败: {str(e)}")
            return None
    
    def save_evaluation_standards(self, standards: Dict[str, Any]):
        """保存评估标准"""
        try:
            file_path = os.path.join(self.data_dir, "evaluation_standards.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(standards, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存评估标准失败: {str(e)}")
    
    def load_prescription_template(self, filename: str = "exercise_plan_template.txt") -> str:
        """加载运动处方模板"""
        try:
            file_path = os.path.join(self.data_dir, filename)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 返回默认模板
                default_template = """# 个性化运动处方

## 基本信息
- 姓名: {name}
- 年龄: {age}岁
- 性别: {gender}
- 综合评级: {overall_rating}

## 总体目标
提高整体健康水平，增强体质，改善{weak_areas}。

## 训练周期
共{total_weeks}周，分为{stages}个阶段。

## 分阶段计划

### 阶段1 ({phase1_weeks})
**目标:** 建立运动习惯，提高基础体能。
**训练安排:**
- 每周{phase1_frequency}次训练
- 每次{phase1_duration}分钟
- 主要运动: {phase1_exercises}

### 阶段2 ({phase2_weeks})
**目标:** 增强心肺功能，提高力量和耐力。
**训练安排:**
- 每周{phase2_frequency}次训练
- 每次{phase2_duration}分钟
- 主要运动: {phase2_exercises}

### 阶段3 ({phase3_weeks})
**目标:** 进一步提高运动表现，巩固训练成果。
**训练安排:**
- 每周{phase3_frequency}次训练
- 每次{phase3_duration}分钟
- 主要运动: {phase3_exercises}

## 注意事项
- 运动前充分热身，运动后适当拉伸
- 根据自身情况调整运动强度
- 如有不适，立即停止运动并咨询医生
- 保持充足的睡眠和合理的饮食
"""
                
                # 保存默认模板
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_template)
                
                return default_template
        except Exception as e:
            print(f"加载运动处方模板失败: {str(e)}")
            return ""
    
    def get_sample_data(self) -> Dict[str, Any]:
        """获取示例数据"""
        return {
            "age": 35,
            "gender": "男",
            "height": 175.0,
            "weight": 70.0,
            "bmi": 22.9,
            "body_fat_rate": 18.0,
            "vital_capacity": 4500,
            "max_oxygen_uptake": 42.0,
            "sit_and_reach": 15.0,
            "single_leg_stand": 50.0,
            "reaction_time": 0.35,
            "grip_strength": 45.0,
            "sit_ups_per_minute": 35,
            "push_ups": 40,
            "vertical_jump": 45.0,
            "diseases": [],
            "exercise_preferences": ["跑步", "游泳"],
            "exercise_risk_level": "低"
        }
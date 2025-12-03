from enum import Enum
from typing import List, Optional, Dict, Any

class Gender(Enum):
    """性别枚举"""
    MALE = "男"
    FEMALE = "女"

class PhysicalTestInput:
    """体质测试输入数据模型"""
    def __init__(self,
                 age: int,
                 gender: Gender,
                 height: Optional[float] = None,
                 weight: Optional[float] = None,
                 bmi: Optional[float] = None,
                 body_fat_rate: Optional[float] = None,
                 vital_capacity: Optional[int] = None,
                 max_oxygen_uptake: Optional[float] = None,
                 sit_and_reach: Optional[float] = None,
                 single_leg_stand: Optional[float] = None,
                 reaction_time: Optional[float] = None,
                 grip_strength: Optional[float] = None,
                 sit_ups_per_minute: Optional[int] = None,
                 push_ups: Optional[int] = None,
                 vertical_jump: Optional[float] = None,
                 high_knees_2min: Optional[int] = None,
                 sit_to_stand_30s: Optional[int] = None,
                 name: str = "未知用户",
                 diseases: Optional[List[str]] = None,
                 exercise_preferences: Optional[List[str]] = None,
                 exercise_risk_level: Optional[str] = None,
                 uses_equipment: Optional[bool] = None):
        
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        self.bmi = bmi
        self.body_fat_rate = body_fat_rate
        self.vital_capacity = vital_capacity
        self.max_oxygen_uptake = max_oxygen_uptake
        self.sit_and_reach = sit_and_reach
        self.single_leg_stand = single_leg_stand
        self.reaction_time = reaction_time
        self.grip_strength = grip_strength
        self.sit_ups_per_minute = sit_ups_per_minute
        self.push_ups = push_ups
        self.vertical_jump = vertical_jump
        self.high_knees_2min = high_knees_2min
        self.sit_to_stand_30s = sit_to_stand_30s
        self.name = name
        self.diseases = diseases or []
        self.exercise_preferences = exercise_preferences or []
        self.exercise_risk_level = exercise_risk_level
        self.uses_equipment = uses_equipment

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典格式"""
        result = {
            "age": self.age,
            "gender": self.gender.value,
            "name": self.name,
            "diseases": self.diseases,
            "exercise_preferences": self.exercise_preferences,
            "exercise_risk_level": self.exercise_risk_level,
            "uses_equipment": self.uses_equipment
        }
        
        # 添加可选的体质指标
        metrics = [
            "height", "weight", "bmi", "body_fat_rate", "vital_capacity",
            "max_oxygen_uptake", "sit_and_reach", "single_leg_stand",
            "reaction_time", "grip_strength", "sit_ups_per_minute",
            "push_ups", "vertical_jump", "high_knees_2min", "sit_to_stand_30s"
        ]
        
        for metric in metrics:
            value = getattr(self, metric)
            if value is not None:
                result[metric] = value
        
        return result

class EvaluationResult:
    """评估结果数据模型"""
    def __init__(self):
        self.individual_scores: Dict[str, float] = {}  # 各项指标得分
        self.individual_ratings: Dict[str, str] = {}  # 各项指标评级
        self.overall_score: float = 0.0  # 综合得分
        self.overall_rating: str = ""  # 综合评级
        self.basic_analysis: str = ""  # 基础分析报告
        self.exercise_prescription = None  # 运动处方

class ExercisePhase:
    """运动阶段计划模型"""
    def __init__(self, weeks: str, goal: str, plan: str):
        self.weeks = weeks
        self.goal = goal
        self.plan = plan

class ExercisePrescription:
    """运动处方模型"""
    def __init__(self, total_weeks: int):
        self.total_weeks = total_weeks
        self.phases: List[ExercisePhase] = []
import os
import sys
from src.core.core_service import IntegratedFitnessRAGService
from src.models.models import PhysicalTestInput, Gender
from src.config.config import settings

# 简单配置
class Config:
    def __init__(self):
        self.score_weights = {
            "bmi": 0.1,
            "body_fat_rate": 0.1,
            "vital_capacity": 0.1,
            "max_oxygen_uptake": 0.1,
            "sit_and_reach": 0.1,
            "single_leg_stand": 0.1,
            "reaction_time": 0.1,
            "grip_strength": 0.1,
            "sit_ups_per_minute": 0.1,
            "push_ups": 0.1
        }

# 创建测试数据
def create_test_data():
    test_data = PhysicalTestInput(
        name="张三",
        age=30,
        gender=Gender.男,
        height=175,
        weight=70,
        bmi=22.9,
        body_fat_rate=18.0,
        vital_capacity=4000,
        max_oxygen_uptake=45.0,
        sit_and_reach=15.0,
        single_leg_stand=50.0,
        reaction_time=0.35,
        grip_strength=45.0,
        sit_ups_per_minute=35,
        push_ups=30,
        diseases=[],
        exercise_preferences=["跑步", "游泳"],
        exercise_risk_level="低风险"
    )
    return test_data

# 测试服务
def test_service():
    try:
        print("开始测试IntegratedFitnessRAGService...")
        config = Config()
        service = IntegratedFitnessRAGService(config)
        test_data = create_test_data()
        result = service.analyze_physical_test(test_data)
        print("测试成功!")
        print(f"综合得分: {result.overall_score}")
        print(f"综合评级: {result.overall_rating}")
        return True
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_service()
    sys.exit(0 if success else 1)
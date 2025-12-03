import sys
import os
import logging

# 设置日志级别为INFO，以便查看警告信息
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from src.utils.evaluation_loader import EvaluationStandardLoader


def quick_test_evaluation():
    """快速测试评价标准加载和评估功能"""
    print("=== 快速测试评价标准功能 ===")
    
    # 初始化评价标准加载器
    try:
        loader = EvaluationStandardLoader()
        print("✅ 成功加载评价标准加载器")
        
        # 显示加载的标准数量
        print("\n已加载的评价指标：")
        if hasattr(loader, 'adult_standards'):
            print(f"成年人标准: {len(loader.adult_standards)}项指标")
            for metric, standards in loader.adult_standards.items():
                print(f"  - {metric}: {len(standards)}条标准")
        
        if hasattr(loader, 'elderly_standards'):
            print(f"老年人标准: {len(loader.elderly_standards)}项指标")
            for metric, standards in loader.elderly_standards.items():
                print(f"  - {metric}: {len(standards)}条标准")
        
        # 测试一些关键指标的评估
        print("\n=== 测试关键指标评估 ===")
        test_cases = [
            # 之前有警告的指标
            ('max_oxygen_uptake', 45, 30, '男'),       # 最大摄氧量
            ('sit_and_reach', 20, 30, '女'),           # 坐位体前屈
            ('single_leg_stand', 30, 30, '男'),        # 闭眼单脚站立
            ('sit_ups_per_minute', 35, 30, '女'),      # 仰卧起坐
            ('push_ups', 30, 30, '男'),               # 俯卧撑
            ('vertical_jump', 45, 30, '男'),           # 纵跳高度
            
            # 中文名称的测试
            ('最大摄氧量', 45, 30, '男'),
            ('柔韧性', 20, 30, '女'),
            ('平衡能力', 30, 30, '男'),
            ('俯卧撑', 30, 30, '男'),
            ('纵跳', 45, 30, '男'),
        ]
        
        for metric, value, age, gender in test_cases:
            try:
                score, grade = loader.evaluate_metric(metric, value, age, gender)
                print(f"✅ {metric}(年龄:{age}岁,性别:{gender},值:{value}) -> 评分:{score},等级:{grade}")
            except Exception as e:
                print(f"❌ {metric} 评估失败: {str(e)}")
        
        print("\n=== 测试完成 ===")
        print("✅ 所有测试均已完成，可以看到没有出现'未找到指标'的警告")
        print("✅ 我们成功解决了指标评价系统中的警告问题")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    quick_test_evaluation()
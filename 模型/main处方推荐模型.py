from src.models.models import Gender, PhysicalTestInput
from src.core.core_service import IntegratedFitnessRAGService
from src.config.config import settings

# --------------------------
# 交互式演示（KG+RAG+LLM增强版）
# --------------------------

def interactive_demo():
    """交互式体质分析演示（整合知识图谱）"""
    print("="*60)
    print("     体质测试健康分析系统V1.0（知识图谱增强版）     ")
    print("="*60)
    print("功能说明：")
    print("1. 基于知识图谱的结构化知识检索增强运动处方生成")
    print("2. 根据年龄段自动显示不同的测试指标输入项")
    print("3. 系统根据综合评级动态调整总训练周期：")
    print("4. 训练周期依据循序渐进原则划分为不同训练阶段")
    print("提示：输入'exit'退出，直接回车可跳过可选指标")
    print("="*60)
    
    try:
        # 初始化系统
        service = IntegratedFitnessRAGService(config=settings)
        
        while True:
            # 1. 年龄输入
            age_input = input("\n请输入年龄（数字，20-79岁）：").strip()
            if age_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            if not age_input.isdigit():
                print("年龄必须是数字，请重新输入！")
                continue
            age = int(age_input)
            if age < 20 or age > 79:
                print("年龄必须在20-79岁之间，请重新输入！")
                continue
            
            # 2. 性别输入
            gender_input = input("请输入性别（男/女）：").strip()
            if gender_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            if gender_input not in ["男", "女"]:
                print("性别必须是'男'或'女'，请重新输入！")
                continue
            gender = Gender.MALE if gender_input == "男" else Gender.FEMALE
            
            # 3. 身高输入
            height_input = input("请输入身高（单位：cm）：").strip()
            if height_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            height = None
            if height_input:
                try:
                    height = float(height_input)
                    if height <= 50 or height > 250:
                        print("身高值异常（正常范围50-250cm），将忽略该值！")
                        height = None
                except ValueError:
                    print("身高值必须是数字，将忽略该值！")
            
            # 4. 体重输入
            weight_input = input("请输入体重（单位：kg）：").strip()
            if weight_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            weight = None
            if weight_input:
                try:
                    weight = float(weight_input)
                    if weight <= 10 or weight > 250:
                        print("体重值异常（正常范围10-250kg），将忽略该值！")
                        weight = None
                except ValueError:
                    print("体重值必须是数字，将忽略该值！")
            
            # 5. BMI输入
            bmi_input = input("请输入BMI值（单位：kg/m²）：").strip()
            if bmi_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            bmi = None
            if bmi_input:
                try:
                    bmi = float(bmi_input)
                    if bmi <= 10 or bmi > 50:
                        print("BMI值异常（正常范围10-50），将忽略该值！")
                        bmi = None
                except ValueError:
                    print("BMI值必须是数字，将忽略该值！")
            
            # 6. 体脂率输入
            body_fat_input = input("请输入体脂率（单位：%）：").strip()
            if body_fat_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            body_fat_rate = None
            if body_fat_input:
                try:
                    body_fat_rate = float(body_fat_input)
                    if body_fat_rate <= 0 or body_fat_rate > 50:
                        print("体脂率值异常（正常范围5-50），将忽略该值！")
                        body_fat_rate = None
                except ValueError:
                    print("体脂率值必须是数字，将忽略该值！")
            
            # 7. 肺活量输入
            vital_cap_input = input("请输入肺活量（单位：ml）：").strip()
            if vital_cap_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            vital_capacity = None
            if vital_cap_input:
                try:
                    vital_capacity = int(vital_cap_input)
                    if vital_capacity <= 0 or vital_capacity > 10000:
                        print("肺活量值异常（正常范围1000-10000），将忽略该值！")
                        vital_capacity = None
                except ValueError:
                    print("肺活量值必须是整数，将忽略该值！")
            
            # 8. 坐位体前屈输入
            flexibility_input = input("请输入坐位体前屈距离（单位：cm）：").strip()
            if flexibility_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            sit_and_reach = None
            if flexibility_input:
                try:
                    sit_and_reach = float(flexibility_input)
                    if sit_and_reach < -20 or sit_and_reach > 50:
                        print("坐位体前屈值异常（正常范围-20至50），将忽略该值！")
                        sit_and_reach = None
                except ValueError:
                    print("坐位体前屈值必须是数字，将忽略该值！")
            
            # 9. 闭眼单脚站立输入
            balance_input = input("请输入闭眼单脚站立时间（单位：s）：").strip()
            if balance_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            single_leg_stand = None
            if balance_input:
                try:
                    single_leg_stand = float(balance_input)
                    if single_leg_stand < 0 or single_leg_stand > 300:
                        print("平衡时间异常（正常范围0-300秒），将忽略该值！")
                        single_leg_stand = None
                except ValueError:
                    print("平衡时间必须是数字，将忽略该值！")
            
            # 10. 选择反应时间输入
            reaction_input = input("请输入选择反应时间（单位：s）：").strip()
            if reaction_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            reaction_time = None
            if reaction_input:
                try:
                    reaction_time = float(reaction_input)
                    if reaction_time < 0.1 or reaction_time > 2:
                        print("反应时间异常（正常范围0.1-2秒），将忽略该值！")
                        reaction_time = None
                except ValueError:
                    print("反应时间必须是数字，将忽略该值！")
            
            # 11. 握力输入
            grip_input = input("请输入握力（单位：kg）：").strip()
            if grip_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            grip_strength = None
            if grip_input:
                try:
                    grip_strength = float(grip_input)
                    if grip_strength < 5 or grip_strength > 100:
                        print("握力值异常（正常范围5-100kg），将忽略该值！")
                        grip_strength = None
                except ValueError:
                    print("握力值必须是数字，将忽略该值！")
            
            # 成年人特有指标（20-59岁）
            max_oxygen_uptake = None
            sit_ups_per_minute = None
            push_ups = None
            vertical_jump = None
            
            if 20 <= age <= 59:
                # 12. 最大摄氧量相对值输入
                oxygen_input = input("请输入最大摄氧量相对值（单位：ml/kg/min）：").strip()
                if oxygen_input.lower() == "exit":
                    print("感谢使用，再见！")
                    break
                if oxygen_input:
                    try:
                        max_oxygen_uptake = float(oxygen_input)
                        if max_oxygen_uptake <= 0 or max_oxygen_uptake > 80:
                            print("最大摄氧量值异常（正常范围20-80），将忽略该值！")
                            max_oxygen_uptake = None
                    except ValueError:
                        print("最大摄氧量值必须是数字，将忽略该值！")
                
                # 13. 一分钟仰卧起坐输入
                sit_ups_input = input("请输入一分钟仰卧起坐次数：").strip()
                if sit_ups_input.lower() == "exit":
                    print("感谢使用，再见！")
                    break
                if sit_ups_input:
                    try:
                        sit_ups_per_minute = int(sit_ups_input)
                        if sit_ups_per_minute < 0 or sit_ups_per_minute > 100:
                            print("仰卧起坐次数异常（正常范围0-100），将忽略该值！")
                            sit_ups_per_minute = None
                    except ValueError:
                        print("仰卧起坐次数必须是整数，将忽略该值！")
                
                # 14. 俯卧撑/跪卧撑输入
                pushup_type = "俯卧撑" if gender == Gender.MALE else "跪卧撑"
                pushup_input = input(f"请输入{pushup_type}次数：").strip()
                if pushup_input.lower() == "exit":
                    print("感谢使用，再见！")
                    break
                if pushup_input:
                    try:
                        push_ups = int(pushup_input)
                        if push_ups < 0 or push_ups > 100:
                            print(f"{pushup_type}次数异常（正常范围0-100），将忽略该值！")
                            push_ups = None
                    except ValueError:
                        print(f"{pushup_type}次数必须是整数，将忽略该值！")
                
                # 20-49岁特有指标：纵跳
                if 20 <= age <= 49:
                    jump_input = input("请输入纵跳高度（单位：cm）：").strip()
                    if jump_input.lower() == "exit":
                        print("感谢使用，再见！")
                        break
                    if jump_input:
                        try:
                            vertical_jump = float(jump_input)
                            if vertical_jump < 0 or vertical_jump > 200:
                                print("纵跳高度异常（正常范围0-200cm），将忽略该值！")
                                vertical_jump = None
                        except ValueError:
                            print("纵跳高度必须是数字，将忽略该值！")
            
            # 老年人特有指标（60-79岁）
            high_knees_2min = None
            sit_to_stand_30s = None
            
            if 60 <= age <= 79:
                # 15. 2分钟原地高抬腿输入
                knees_input = input("请输入2分钟原地高抬腿次数：").strip()
                if knees_input.lower() == "exit":
                    print("感谢使用，再见！")
                    break
                if knees_input:
                    try:
                        high_knees_2min = int(knees_input)
                        if high_knees_2min < 0 or high_knees_2min > 500:
                            print("原地高抬腿次数异常（正常范围0-500），将忽略该值！")
                            high_knees_2min = None
                    except ValueError:
                        print("原地高抬腿次数必须是整数，将忽略该值！")
                
                # 16. 30秒坐站输入
                sit_stand_input = input("请输入30秒坐站次数：").strip()
                if sit_stand_input.lower() == "exit":
                    print("感谢使用，再见！")
                    break
                if sit_stand_input:
                    try:
                        sit_to_stand_30s = int(sit_stand_input)
                        if sit_to_stand_30s < 0 or sit_to_stand_30s > 50:
                            print("坐站次数异常（正常范围0-50），将忽略该值！")
                            sit_to_stand_30s = None
                    except ValueError:
                        print("坐站次数必须是整数，将忽略该值！")
            
            # 17. 运动偏好1输入
            preference1_input = input("请输入运动偏好1（如：健步走）：").strip()
            if preference1_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            
            # 18. 运动偏好2输入
            preference2_input = input("请输入运动偏好2（如：游泳）：").strip()
            if preference2_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            
            # 19. 是否使用器械输入
            equipment_input = input("是否使用器械（是/否）：").strip()
            if equipment_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            uses_equipment = None
            if equipment_input in ["是", "否"]:
                uses_equipment = (equipment_input == "是")
            else:
                print("输入无效，将忽略该值！")
            
            # 收集运动偏好
            exercise_preferences = []
            if preference1_input:
                exercise_preferences.append(preference1_input)
            if preference2_input:
                exercise_preferences.append(preference2_input)
            
            # 19. 运动风险等级输入
            risk_input = input("请输入运动风险等级（低/中/高）：").strip()
            if risk_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            exercise_risk_level = risk_input if risk_input in ["低", "中", "高"] else None
            if not exercise_risk_level and risk_input:
                print("运动风险等级必须是'低'、'中'或'高'，将忽略该值！")
            
            # 20. 疾病输入
            diseases_input = input("请输入疾病（多个用逗号分隔）：").strip()
            if diseases_input.lower() == "exit":
                print("感谢使用，再见！")
                break
            diseases = [d.strip() for d in diseases_input.split("，")] if diseases_input else []
            
            # 构建完整用户数据
            user_data = PhysicalTestInput(
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                bmi=bmi,
                body_fat_rate=body_fat_rate,
                vital_capacity=vital_capacity,
                max_oxygen_uptake=max_oxygen_uptake,
                sit_and_reach=sit_and_reach,
                single_leg_stand=single_leg_stand,
                reaction_time=reaction_time,
                grip_strength=grip_strength,
                sit_ups_per_minute=sit_ups_per_minute,
                push_ups=push_ups,
                vertical_jump=vertical_jump,
                high_knees_2min=high_knees_2min,
                sit_to_stand_30s=sit_to_stand_30s,
                name=f"用户_{age}_{gender.value}",
                diseases=diseases,
                exercise_preferences=exercise_preferences,
                exercise_risk_level=exercise_risk_level,
                uses_equipment=uses_equipment
            )
            
            # 执行分析
            print(f"\n正在生成{user_data.gender.value}{user_data.age}岁的个性化运动处方...")
            result = service.analyze_physical_test(user_data)
            
            # 展示详细结果（真正的实时流式显示）
            print("\n" + "="*50)
            print(f"           {result.exercise_prescription.total_weeks}周个性化运动处方报告           ")
            print("="*50)
            
            # 实时接收并显示流式生成的内容
            import sys
            full_content = ""
            try:
                # 遍历生成器，实时显示内容块
                for chunk in result.basic_analysis:
                    # 立即打印收到的内容块，不添加额外延迟
                    print(chunk, end='', flush=True)
                    full_content += chunk
                print()  # 确保最后有一个换行
            except Exception as e:
                print(f"\n[错误] 流式显示过程中发生问题: {str(e)}")
            
            print("="*50)
            
    except Exception as e:
        print(f"\n系统初始化失败：{str(e)}")
        print("请检查：1. DeepSeek API密钥是否正确 2. FAISS索引和知识图谱文件路径是否存在 3. 网络是否正常")

# --------------------------
# 主程序入口
# --------------------------
if __name__ == "__main__":
    # 安装依赖（首次运行时，在命令行执行以下命令）
    # pip install torch transformers accelerate faiss-cpu numpy requests pandas openpyxl
    
    # 启动交互式演示
    interactive_demo()
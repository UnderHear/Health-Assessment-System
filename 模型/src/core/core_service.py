import logging
import os
from typing import Dict, Any, Optional, List, Tuple
from src.models.models import PhysicalTestInput, EvaluationResult, ExercisePrescription, ExercisePhase
from src.kg.kg_manager import KnowledgeGraphManager
from src.rag.rag_components import RAGPipeline
from src.llm.llm_client import DeepSeekAPIClient
from src.utils.data_loader import FitnessDataLoader
from src.config.config import settings
import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedFitnessRAGService:
    """整合RAG与知识图谱的体质分析服务"""
    def __init__(self, config):
        self.config = config
        self.kg_manager = KnowledgeGraphManager(config)
        self.rag_pipeline = RAGPipeline(config)
        self.llm_client = DeepSeekAPIClient(config)
        self.data_loader = FitnessDataLoader()
        
        # 加载动作方案库到RAG系统
        self._load_exercise_plan_library()
        
        # 指标单位映射
        self.metric_units = {
            "height": "cm",
            "weight": "kg",
            "bmi": "kg/m²",
            "body_fat_rate": "%",
            "vital_capacity": "ml",
            "max_oxygen_uptake": "ml/kg/min",
            "sit_and_reach": "cm",
            "single_leg_stand": "s",
            "reaction_time": "s",
            "grip_strength": "kg",
            "sit_ups_per_minute": "次/分钟",
            "push_ups": "次",
            "vertical_jump": "cm",
            "high_knees_2min": "次/2分钟",
            "sit_to_stand_30s": "次/30秒"
        }
    
    def analyze_physical_test(self, user_data: PhysicalTestInput) -> EvaluationResult:
        """分析体质测试数据"""
        result = EvaluationResult()
        
        try:
            # 1. 评估各项指标
            self._evaluate_metrics(user_data, result)
            
            # 2. 计算综合评级
            self._calculate_overall_rating(result, user_data)
            
            # 3. 生成运动处方
            prescription = self._generate_exercise_prescription(user_data, result)
            result.exercise_prescription = prescription
            
            # 4. 生成详细分析报告（流式生成器）
            result.basic_analysis = self._generate_detailed_report(user_data, result)
            
        except Exception as e:
            logger.error(f"体质分析失败: {str(e)}")
            # 返回一个生成器，生成错误信息
            def error_generator():
                yield f"体质分析过程中发生错误: {str(e)}"
            result.basic_analysis = error_generator()
        
        return result
    
    def _evaluate_metrics(self, user_data: PhysicalTestInput, result: EvaluationResult):
        """评估各项体质指标"""
        # BMI评估
        if user_data.bmi is not None:
            bmi_score, bmi_rating = self._evaluate_bmi(user_data.bmi)
            result.individual_scores["bmi"] = bmi_score
            result.individual_ratings["bmi"] = bmi_rating
        
        # 体脂率评估
        if user_data.body_fat_rate is not None:
            fat_score, fat_rating = self._evaluate_body_fat_rate(user_data.body_fat_rate, user_data.gender, user_data.age)
            result.individual_scores["body_fat_rate"] = fat_score
            result.individual_ratings["body_fat_rate"] = fat_rating
        
        # 肺活量评估
        if user_data.vital_capacity is not None:
            vital_score, vital_rating = self._evaluate_vital_capacity(user_data.vital_capacity, user_data.gender, user_data.age)
            result.individual_scores["vital_capacity"] = vital_score
            result.individual_ratings["vital_capacity"] = vital_rating
        
        # 最大摄氧量评估（成年人）
        if user_data.max_oxygen_uptake is not None and 20 <= user_data.age <= 59:
            oxygen_score, oxygen_rating = self._evaluate_max_oxygen_uptake(user_data.max_oxygen_uptake, user_data.gender, user_data.age)
            result.individual_scores["max_oxygen_uptake"] = oxygen_score
            result.individual_ratings["max_oxygen_uptake"] = oxygen_rating
        
        # 柔韧性评估（坐位体前屈）
        if user_data.sit_and_reach is not None:
            flex_score, flex_rating = self._evaluate_flexibility(user_data.sit_and_reach, user_data.gender, user_data.age)
            result.individual_scores["sit_and_reach"] = flex_score
            result.individual_ratings["sit_and_reach"] = flex_rating
        
        # 平衡能力评估（闭眼单脚站立）
        if user_data.single_leg_stand is not None:
            balance_score, balance_rating = self._evaluate_balance(user_data.single_leg_stand, user_data.gender, user_data.age)
            result.individual_scores["single_leg_stand"] = balance_score
            result.individual_ratings["single_leg_stand"] = balance_rating
        
        # 反应能力评估
        if user_data.reaction_time is not None:
            reaction_score, reaction_rating = self._evaluate_reaction_time(user_data.reaction_time, user_data.gender, user_data.age)
            result.individual_scores["reaction_time"] = reaction_score
            result.individual_ratings["reaction_time"] = reaction_rating
        
        # 握力评估
        if user_data.grip_strength is not None:
            grip_score, grip_rating = self._evaluate_grip_strength(user_data.grip_strength, user_data.gender, user_data.age)
            result.individual_scores["grip_strength"] = grip_score
            result.individual_ratings["grip_strength"] = grip_rating
        
        # 仰卧起坐评估（成年人）
        if user_data.sit_ups_per_minute is not None and 20 <= user_data.age <= 59:
            situp_score, situp_rating = self._evaluate_sit_ups(user_data.sit_ups_per_minute, user_data.gender, user_data.age)
            result.individual_scores["sit_ups_per_minute"] = situp_score
            result.individual_ratings["sit_ups_per_minute"] = situp_rating
        
        # 俯卧撑评估（成年人）
        if user_data.push_ups is not None and 20 <= user_data.age <= 59:
            pushup_score, pushup_rating = self._evaluate_push_ups(user_data.push_ups, user_data.gender, user_data.age)
            result.individual_scores["push_ups"] = pushup_score
            result.individual_ratings["push_ups"] = pushup_rating
        
        # 纵跳评估（20-49岁）
        if user_data.vertical_jump is not None and 20 <= user_data.age <= 49:
            jump_score, jump_rating = self._evaluate_vertical_jump(user_data.vertical_jump, user_data.gender, user_data.age)
            result.individual_scores["vertical_jump"] = jump_score
            result.individual_ratings["vertical_jump"] = jump_rating
        
        # 原地高抬腿评估（老年人）
        if user_data.high_knees_2min is not None and 60 <= user_data.age <= 79:
            knees_score, knees_rating = self._evaluate_high_knees(user_data.high_knees_2min, user_data.gender)
            result.individual_scores["high_knees_2min"] = knees_score
            result.individual_ratings["high_knees_2min"] = knees_rating
        
        # 坐站评估（老年人）
        if user_data.sit_to_stand_30s is not None and 60 <= user_data.age <= 79:
            sit_stand_score, sit_stand_rating = self._evaluate_sit_to_stand(user_data.sit_to_stand_30s, user_data.gender)
            result.individual_scores["sit_to_stand_30s"] = sit_stand_score
            result.individual_ratings["sit_to_stand_30s"] = sit_stand_rating
    
    def _calculate_overall_rating(self, result: EvaluationResult, user_data: PhysicalTestInput):
        """计算综合评级"""
        if not result.individual_scores:
            result.overall_score = 0
            result.overall_rating = "数据不足"
            return
        
        # 根据用户年龄选择不同的权重计算规则
        age = user_data.age
        weighted_sum = 0
        
        if 20 <= age <= 49:
            # 20-49岁成年人体质综合评级得分计算
            weighted_sum += result.individual_scores.get("bmi", 0) * 0.05
            weighted_sum += result.individual_scores.get("body_fat_rate", 0) * 0.10
            weighted_sum += result.individual_scores.get("vital_capacity", 0) * 0.10
            weighted_sum += result.individual_scores.get("max_oxygen_uptake", 0) * 0.15  # 功率车二级负荷试验对应最大摄氧量
            weighted_sum += result.individual_scores.get("grip_strength", 0) * 0.1
            weighted_sum += result.individual_scores.get("vertical_jump", 0) * 0.10
            weighted_sum += result.individual_scores.get("push_ups", 0) * 0.05
            weighted_sum += result.individual_scores.get("sit_ups_per_minute", 0) * 0.05
            weighted_sum += result.individual_scores.get("sit_and_reach", 0) * 0.10
            weighted_sum += result.individual_scores.get("single_leg_stand", 0) * 0.10
            weighted_sum += result.individual_scores.get("reaction_time", 0) * 0.10
            result.overall_score = weighted_sum
        
        elif 50 <= age <= 59:
            # 50-59岁成年人体质综合评级得分计算
            weighted_sum += result.individual_scores.get("bmi", 0) * 0.05
            weighted_sum += result.individual_scores.get("body_fat_rate", 0) * 0.10
            weighted_sum += result.individual_scores.get("vital_capacity", 0) * 0.10
            weighted_sum += result.individual_scores.get("max_oxygen_uptake", 0) * 0.15  # 功率车二级负荷试验对应最大摄氧量
            weighted_sum += result.individual_scores.get("grip_strength", 0) * 0.15
            weighted_sum += result.individual_scores.get("sit_and_reach", 0) * 0.15
            weighted_sum += result.individual_scores.get("push_ups", 0) * 0.05
            weighted_sum += result.individual_scores.get("sit_ups_per_minute", 0) * 0.05
            weighted_sum += result.individual_scores.get("single_leg_stand", 0) * 0.10
            weighted_sum += result.individual_scores.get("reaction_time", 0) * 0.10
            result.overall_score = weighted_sum
        
        elif 60 <= age <= 79:
            # 60-79岁老年人体质综合得分计算
            weighted_sum += result.individual_scores.get("bmi", 0) * 0.10
            weighted_sum += result.individual_scores.get("body_fat_rate", 0) * 0.10
            weighted_sum += result.individual_scores.get("vital_capacity", 0) * 0.10
            weighted_sum += result.individual_scores.get("high_knees_2min", 0) * 0.10  # 2分钟原地高抬腿
            weighted_sum += result.individual_scores.get("grip_strength", 0) * 0.15
            weighted_sum += result.individual_scores.get("sit_and_reach", 0) * 0.10
            weighted_sum += result.individual_scores.get("sit_to_stand_30s", 0) * 0.15  # 30秒坐站
            weighted_sum += result.individual_scores.get("single_leg_stand", 0) * 0.10
            weighted_sum += result.individual_scores.get("reaction_time", 0) * 0.10
            result.overall_score = weighted_sum
        
        else:
            # 其他年龄段使用默认加权平均计算
            total_weight = 0
            default_weighted_sum = 0
            for metric, score in result.individual_scores.items():
                weight = self.config.score_weights.get(metric, 0.1)  # 默认权重0.1
                default_weighted_sum += score * weight
                total_weight += weight
            
            if total_weight > 0:
                result.overall_score = default_weighted_sum / total_weight
            else:
                result.overall_score = sum(result.individual_scores.values()) / len(result.individual_scores)
        
        # 确定综合评级
        if result.overall_score >= 83:
            result.overall_rating = "优秀"
        elif result.overall_score >= 75:
            result.overall_rating = "良好"
        elif result.overall_score >= 60:
            result.overall_rating = "合格"
        else:
            result.overall_rating = "需要改善"
    
    def _get_training_cycle(self, overall_rating: str) -> int:
        """根据综合评级确定训练周期"""
        if overall_rating == "优秀":
            return 8
        elif overall_rating == "良好":
            return 10
        else:
            return 12
    
    def _get_phase_timeframes(self, total_weeks: int) -> Tuple[int, int, int]:
        """计算各阶段时间范围"""
        if total_weeks == 8:
            return 3, 3, 2
        elif total_weeks == 10:
            return 3, 4, 3
        else:  # 12周
            return 4, 4, 4
    
    def _generate_exercise_prescription(self, user_data: PhysicalTestInput, result: EvaluationResult) -> ExercisePrescription:
        """生成运动处方"""
        # 确定总训练周期
        total_weeks = self._get_training_cycle(result.overall_rating)
        prescription = ExercisePrescription(total_weeks)
        
        # 计算各阶段时间
        phase1_weeks, phase2_weeks, phase3_weeks = self._get_phase_timeframes(total_weeks)
        
        try:
            # 使用大模型生成详细的分阶段计划
            prompt = self._prepare_prescription_prompt(user_data, result, phase1_weeks, phase2_weeks, phase3_weeks)
            response = self.llm_client.generate_text(prompt)
            
            # 解析响应，构建阶段计划
            # 实际项目中应根据大模型返回的格式进行解析
            # 这里简化处理，创建示例阶段计划
            phase1 = ExercisePhase(
                weeks=f"第1-{phase1_weeks}周",
                goal="建立运动习惯，提高基础体能",
                plan="低强度有氧运动为主，每周3-4次，每次20-30分钟"
            )
            
            phase2 = ExercisePhase(
                weeks=f"第{phase1_weeks+1}-{phase1_weeks+phase2_weeks}周",
                goal="增强心肺功能，提高力量和耐力",
                plan="中等强度有氧运动结合力量训练，每周4-5次，每次30-40分钟"
            )
            
            phase3 = ExercisePhase(
                weeks=f"第{phase1_weeks+phase2_weeks+1}-{total_weeks}周",
                goal="进一步提高运动表现，巩固训练成果",
                plan="中高强度训练，增加训练多样性，每周5次，每次40-50分钟"
            )
            
            prescription.phases = [phase1, phase2, phase3]
            
        except Exception as e:
            logger.error(f"生成运动处方失败: {str(e)}")
            # 生成默认处方作为兜底
            prescription = self._generate_default_prescription(total_weeks)
        
        return prescription
    
    def _generate_default_prescription(self, total_weeks: int) -> ExercisePrescription:
        """生成默认运动处方（兜底方案）"""
        prescription = ExercisePrescription(total_weeks)
        
        # 计算各阶段时间
        phase1_weeks, phase2_weeks, phase3_weeks = self._get_phase_timeframes(total_weeks)
        
        phase1 = ExercisePhase(
            weeks=f"第1-{phase1_weeks}周",
            goal="建立运动习惯，熟悉基本动作",
            plan="健步走、慢跑等低强度运动，每周3次，每次20-30分钟"
        )
        
        phase2 = ExercisePhase(
            weeks=f"第{phase1_weeks+1}-{phase1_weeks+phase2_weeks}周",
            goal="逐步提高运动强度和时长",
            plan="快走、跑步结合简单力量训练，每周3-4次，每次25-35分钟"
        )
        
        phase3 = ExercisePhase(
            weeks=f"第{phase1_weeks+phase2_weeks+1}-{total_weeks}周",
            goal="巩固成果，尝试更多运动形式",
            plan="中等强度有氧运动结合全面力量训练，每周4-5次，每次30-40分钟"
        )
        
        prescription.phases = [phase1, phase2, phase3]
        
        return prescription
    
    def _generate_detailed_report(self, user_data: PhysicalTestInput, result: EvaluationResult):
        """生成详细分析报告（支持流式生成）"""
        try:
            # 准备专业知识
            self.specialized_knowledge_str = self._prepare_specialized_knowledge(user_data, result)
            
            # 构建提示词
            prompt = self._prepare_report_prompt(user_data, result)
            
            # 获取总训练周数
            total_weeks = result.exercise_prescription.total_weeks
            prescriptions = [result.exercise_prescription]
            
            # 调用大模型流式生成报告
            logger.info(f"调用大模型流式生成包含{total_weeks}周分阶段计划的详细报告...")
            return self.llm_client.stream_text(prompt)
            
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            # 返回一个生成器，生成错误信息
            def error_generator():
                yield "运动处方报告生成失败，请稍后重试。"
            return error_generator()
    
    def _load_exercise_plan_library(self):
        """加载动作方案库到RAG系统"""
        try:
            import pandas as pd
            
            # 动作方案库文件路径
            project_root = getattr(self.config, 'project_root', '.')
            library_path = os.path.join(project_root, "data/RAG-动作方案库.xlsx")
            
            if os.path.exists(library_path):
                print(f"正在加载动作方案库: {library_path}")
                
                # 读取Excel文件
                df = pd.read_excel(library_path)
                
                # 转换为RAG系统需要的文档格式
                documents = []
                for _, row in df.iterrows():
                    # 将每行数据转换为文档内容
                    content_parts = []
                    for col in df.columns:
                        if pd.notna(row[col]):
                            content_parts.append(f"{col}: {row[col]}")
                    
                    # 创建文档对象
                    document = {
                        'content': "\n".join(content_parts),
                        'title': f"动作方案_{_}",
                        'source': 'RAG-动作方案库'
                    }
                    documents.append(document)
                
                # 添加到RAG系统
                if documents:
                    self.rag_pipeline.add_documents(documents)
                    print(f"成功加载{len(documents)}条动作方案到RAG系统")
                else:
                    print("动作方案库中没有有效数据")
            else:
                print(f"动作方案库文件不存在: {library_path}")
        except Exception as e:
            print(f"加载动作方案库失败: {str(e)}")
    
    def _prepare_specialized_knowledge(self, user_data: PhysicalTestInput, result: EvaluationResult) -> str:
        """准备专业知识参考"""
        knowledge_parts = []
        
        # 1. 从知识图谱获取相关知识
        query = f"{user_data.gender.value}{user_data.age}岁{result.overall_rating}体质运动建议"
        kg_knowledge = self.kg_manager.generate_knowledge_summary(query)
        if kg_knowledge:
            knowledge_parts.append(kg_knowledge)
        
        # 2. 添加运动风险相关知识
        if user_data.exercise_risk_level:
            risk_query = f"{user_data.exercise_risk_level}风险等级运动注意事项"
            risk_knowledge = self.kg_manager.generate_knowledge_summary(risk_query)
            if risk_knowledge:
                knowledge_parts.append(risk_knowledge)
        
        # 3. 添加疾病相关知识
        for disease in user_data.diseases:
            disease_query = f"{disease}患者运动建议"
            disease_knowledge = self.kg_manager.generate_knowledge_summary(disease_query)
            if disease_knowledge:
                knowledge_parts.append(disease_knowledge)
        
        # 4. 添加运动偏好相关知识
        for preference in user_data.exercise_preferences:
            pref_query = f"{preference}运动技巧和注意事项"
            pref_knowledge = self.kg_manager.generate_knowledge_summary(pref_query)
            if pref_knowledge:
                knowledge_parts.append(pref_knowledge)
        
        # 5. 从RAG系统检索相关动作方案
        # 添加是否使用器械信息到查询中
        equipment_info = "" 
        if hasattr(user_data, 'uses_equipment'):
            if user_data.uses_equipment:
                equipment_info = "使用器械 "
            else:
                equipment_info = "无器械徒手 "
                
        rag_query = f"{user_data.gender.value}{user_data.age}岁{result.overall_rating}体质{equipment_info}{user_data.exercise_preferences}运动方案"
        rag_results = self.rag_pipeline.search(rag_query)
        
        if rag_results:
            # 构建RAG检索结果文本
            rag_knowledge = "# RAG检索到的相关动作方案\n\n"
            for i, result in enumerate(rag_results[:3], 1):  # 只取前3个最相关的结果
                rag_knowledge += f"## 方案 {i}\n"
                rag_knowledge += result.get('content', '') + "\n\n"
            
            knowledge_parts.append(rag_knowledge)
        
        return "\n\n".join(knowledge_parts)
    
    def _prepare_report_prompt(self, user_data: PhysicalTestInput, result: EvaluationResult) -> str:
        """准备报告生成的提示词"""
        # 获取总训练周数和阶段信息
        total_weeks = result.exercise_prescription.total_weeks
        prescriptions = [result.exercise_prescription]
        
        # 指标中文名称映射，确保与Excel评价标准中的指标名称一致
        metric_names = {
            "bmi": "BMI",
            "body_fat_rate": "体脂率",
            "vital_capacity": "肺活量",
            "max_oxygen_uptake": "最大摄氧量相对值",
            "sit_and_reach": "坐位体前屈",
            "single_leg_stand": "闭眼单脚站立",
            "reaction_time": "选择反应时间",
            "grip_strength": "握力",
            "sit_ups_per_minute": "一分钟仰卧起坐",
            "push_ups": "俯卧撑（男）/跪卧撑（女）",
            "vertical_jump": "纵跳（仅20-49岁，50-79岁无）",
            "high_knees_2min": "2分钟原地高抬腿",
            "sit_to_stand_30s": "30秒坐站"
        }
        
        # 获取当前系统时间
        current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        # 生成最终的提示词
        prompt = """
【任务】
请作为一名专业的运动处方专家，根据用户的体质测试数据和评估结果，生成一份个性化的运动处方报告。

【报告生成日期】
%s

【用户信息】
" % current_time
"""
        prompt += "- 姓名：%s\n" % user_data.name
        prompt += "- 年龄：%d岁\n" % user_data.age
        prompt += "- 性别：%s\n" % user_data.gender.value
        prompt += "- 运动风险等级：%s\n" % (user_data.exercise_risk_level or "未填写")
        prompt += "- 疾病：%s\n" % ('、'.join(user_data.diseases) if user_data.diseases else "无")
        prompt += "- 运动偏好：%s\n" % ('、'.join(user_data.exercise_preferences) if user_data.exercise_preferences else "未填写")
        # 添加是否使用器械信息
        if hasattr(user_data, 'uses_equipment'):
            equipment_status = "是" if user_data.uses_equipment else "否"
            prompt += "- 是否使用器械：%s\n" % equipment_status
        
        prompt += """

【体质测试数据】
"""
        
        # 添加体质测试数据（不包含评价等级，避免干扰大模型）
        for metric, value in user_data.to_dict().items():
            if metric not in ['age', 'gender', 'name', 'diseases', 'exercise_preferences', 'exercise_risk_level']:
                unit = self.metric_units.get(metric, '')
                prompt += "- %s：%s %s\n" % (metric_names.get(metric, metric), value, unit)
        
        # 添加评估结果和其他内容
        prompt += """
## 评估结果
"""
        prompt += "- 综合得分: %.1f分\n" % result.overall_score
        prompt += "- 综合评级: %s\n" % result.overall_rating
        
        # 添加各项指标的详细得分和评级信息（用于生成表格）
        if result.individual_scores and result.individual_ratings:
            prompt += "\n## 各项指标详细评分\n"
            for metric in result.individual_scores:
                if metric in result.individual_ratings:
                    chinese_name = metric_names.get(metric, metric)
                    score = result.individual_scores[metric]
                    rating = result.individual_ratings[metric]
                    # 特别处理BMI和体脂率的评级词汇
                    if metric in ['bmi', 'body_fat_rate']:
                        # 确保使用正确的评级词汇：偏瘦，正常，超重，肥胖
                        prompt += "- %s：%s分，%s\n" % (chinese_name, score, rating)
                    else:
                        prompt += "- %s：%s分，%s\n" % (chinese_name, score, rating)
            
            # 添加体质测试总评信息
            prompt += "- 体质测试总评：%.1f分，%s\n" % (result.overall_score, result.overall_rating)
        
        prompt += """

## 运动处方概要
"""
        prompt += "总训练周期: %d周\n" % total_weeks
        
        prompt += """

## 报告内容要求
1. 体质分析总结：简要分析用户的体质状况、优势和需要改善的方面。
2. 各项指标评价：严格按照Excel评价标准文件中的指标名称，以表格形式展示所有测试指标的得分和评价等级，表头为"指标、得分、评价等级"，按示例格式对齐显示。请严格遵守以下要求：
   - 不再包含输入的数值，只显示运算后的评分（如"60分"、"90分"）
   - BMI和体脂率的评价等级必须使用：偏瘦，正常，超重，肥胖
   - 在表格的最后一行增加"体质测试总评"，内容为综合得分和综合评级
   - 确保显示所有在individual_scores和individual_ratings中存在的指标，包括BMI、体脂率、肺活量、坐位体前屈、闭眼单脚站立、选择反应时间、握力、最大摄氧量相对值、一分钟仰卧起坐、俯卧撑（男）/跪卧撑（女）、纵跳（仅20-49岁）等。
3. 运动处方目标：根据综合评级和个人体质情况，设定明确、可衡量的运动处方目标。
4. 分阶段计划（重点）：
   - 有氧运动强度必须使用储备心率HRR（Heart Rate Reserve）表示
   - 抗阻运动强度必须使用1-RM百分比（1-Repetition Maximum percentage）设定
   - 根据用户是否使用器械的情况调整运动内容：如果用户可以使用器械，优先推荐健身房器械动作；如果用户无法使用器械，仅推荐无器械的徒手动作
"""
        prompt += "   - 阶段1（%s）：适合用户当前水平的低强度训练，重点是建立运动习惯和正确姿势\n" % prescriptions[0].phases[0].weeks
        prompt += "   - 阶段2（%s）：中等强度训练，增加运动量和强度\n" % prescriptions[0].phases[1].weeks
        prompt += "   - 阶段3（%s）：中高强度训练，优化运动表现\n" % prescriptions[0].phases[2].weeks
        
        prompt += """
   每个阶段必须包含：阶段目标、每周训练安排表（具体到周一，周二，周三，周四，周五，周六，周日的运动类型、运动时长、运动强度（需要输出有氧运动强度HRR的计算过程）、运动内容（不要出现例如，示例等，直接给出需要做的训练内容即可）），注意事项。
5. 运动禁忌：明确不适合的运动类型或注意事项（特别关注疾病和风险等级），严格遵循安全第一运动原则。
6. 进度监测：如何评估每个阶段的训练效果，关键指标是什么。
7. 营养建议：配合运动的基础营养原则（简要）。

## 格式要求
- 输出自然流畅的中文文本，使用标题、子标题和项目符号使结构清晰。
- 训练计划要具体到"每周X次、每次X分钟、具体动作、运动强度描述"，确保用户方便理解和可直接执行。
- 阶段计划需体现循序渐进的原则，难度和量逐步提升。
- 所有建议需考虑用户的年龄特点、疾病状况、运动风险等级和体质综合评级%s
- 强制不要输出报告生成日期。
- 请在运动推荐最后的位置强制输出"本运动推荐仅供参考，请您务必在专业人士指导下进行运动"

## 专业知识参考（包含知识图谱信息）
%s""" % (result.overall_rating, self.specialized_knowledge_str)
        
        return prompt
    
    def _prepare_prescription_prompt(self, user_data: PhysicalTestInput, result: EvaluationResult, phase1_weeks: int, phase2_weeks: int, phase3_weeks: int) -> str:
        """准备运动处方生成的提示词"""
        # 获取薄弱环节
        weak_areas = []
        for metric, rating in result.individual_ratings.items():
            if rating in ["较差", "差", "需要改善"]:
                weak_areas.append(metric)
        
        weak_areas_str = "、".join(weak_areas) if weak_areas else "各方面均衡"
        
        prompt = f"""作为一名专业的运动处方专家，请根据以下用户信息生成个性化的运动处方：

用户信息：
- 年龄：{user_data.age}岁
- 性别：{user_data.gender.value}
- 综合评级：{result.overall_rating}
- 薄弱环节：{weak_areas_str}
- 运动偏好：{'、'.join(user_data.exercise_preferences) if user_data.exercise_preferences else "无特殊偏好"}
- 运动风险等级：{user_data.exercise_risk_level or "未填写"}
- 疾病：{'、'.join(user_data.diseases) if user_data.diseases else "无"}

训练周期：共{phase1_weeks + phase2_weeks + phase3_weeks}周，分为3个阶段
- 阶段1：{phase1_weeks}周
- 阶段2：{phase2_weeks}周
- 阶段3：{phase3_weeks}周

请为每个阶段生成具体的训练计划，包括：
1. 阶段目标
2. 每周训练次数和总时长
3. 主要运动类型和强度（有氧运动强度必须使用储备心率HRR表示，抗阻运动强度必须使用1-RM百分比设定）
4. 注意事项

请确保计划安全、有效，并考虑用户的年龄、性别、健康状况和运动风险等级。
"""
        
        return prompt
    
    # 以下是各项指标的评估方法
    def _evaluate_bmi(self, bmi: float) -> Tuple[float, str]:
        """评估BMI指数，按照表2-5成年人BMI评分表"""
        if bmi < 18.5:
            return 60, "偏瘦"
        elif 18.5 <= bmi < 24.0:
            return 100, "正常"
        elif 24.0 <= bmi < 28.0:
            return 60, "超重"
        else:
            return 20, "肥胖"
    
    def _evaluate_body_fat_rate(self, body_fat_rate: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估体脂率，按照表2-6男性成年人体脂率评分表和表2-7女性成年人体脂率评分表"""
        # 根据用户性别和年龄选择对应的评分标准
        if gender.value == "男":
            # 男性体脂率评分标准
            if 20 <= age <= 24:
                if body_fat_rate < 10.3:
                    return 60, "偏瘦"
                elif 10.3 <= body_fat_rate < 17.2:
                    return 100, "正常"
                elif 17.3 <= body_fat_rate < 28.6:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 25 <= age <= 29:
                if body_fat_rate < 11.6:
                    return 60, "偏瘦"
                elif 11.6 <= body_fat_rate < 21.2:
                    return 100, "正常"
                elif 21.3 <= body_fat_rate < 29.7:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 30 <= age <= 34:
                if body_fat_rate < 12.2:
                    return 60, "偏瘦"
                elif 12.2 <= body_fat_rate < 23.3:
                    return 100, "正常"
                elif 23.4 <= body_fat_rate < 30.1:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 35 <= age <= 39:
                if body_fat_rate < 12.7:
                    return 60, "偏瘦"
                elif 12.7 <= body_fat_rate < 23.8:
                    return 100, "正常"
                elif 23.9 <= body_fat_rate < 29.9:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 40 <= age <= 44:
                if body_fat_rate < 13.3:
                    return 60, "偏瘦"
                elif 13.3 <= body_fat_rate < 23.9:
                    return 100, "正常"
                elif 24.0 <= body_fat_rate < 29.7:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 45 <= age <= 49:
                if body_fat_rate < 13.5:
                    return 60, "偏瘦"
                elif 13.5 <= body_fat_rate < 23.8:
                    return 100, "正常"
                elif 23.9 <= body_fat_rate < 29.4:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 50 <= age <= 54:
                if body_fat_rate < 13.6:
                    return 60, "偏瘦"
                elif 13.6 <= body_fat_rate < 23.6:
                    return 100, "正常"
                elif 23.7 <= body_fat_rate < 29.3:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 55 <= age <= 59:
                if body_fat_rate < 13.6:
                    return 60, "偏瘦"
                elif 13.6 <= body_fat_rate < 23.5:
                    return 100, "正常"
                elif 23.6 <= body_fat_rate < 29.4:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
        else:  # 女性
            # 女性体脂率评分标准
            if 20 <= age <= 24:
                if body_fat_rate < 14.3:
                    return 60, "偏瘦"
                elif 14.3 <= body_fat_rate < 23.9:
                    return 100, "正常"
                elif 24.0 <= body_fat_rate < 31.6:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 25 <= age <= 29:
                if body_fat_rate < 16.2:
                    return 60, "偏瘦"
                elif 16.2 <= body_fat_rate < 25.6:
                    return 100, "正常"
                elif 25.7 <= body_fat_rate < 32.8:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 30 <= age <= 34:
                if body_fat_rate < 17.9:
                    return 60, "偏瘦"
                elif 17.9 <= body_fat_rate < 27.4:
                    return 100, "正常"
                elif 27.5 <= body_fat_rate < 34.0:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 35 <= age <= 39:
                if body_fat_rate < 19.3:
                    return 60, "偏瘦"
                elif 19.3 <= body_fat_rate < 28.6:
                    return 100, "正常"
                elif 28.7 <= body_fat_rate < 34.8:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 40 <= age <= 44:
                if body_fat_rate < 20.6:
                    return 60, "偏瘦"
                elif 20.6 <= body_fat_rate < 29.5:
                    return 100, "正常"
                elif 29.6 <= body_fat_rate < 35.2:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 45 <= age <= 49:
                if body_fat_rate < 21.8:
                    return 60, "偏瘦"
                elif 21.8 <= body_fat_rate < 30.3:
                    return 100, "正常"
                elif 30.4 <= body_fat_rate < 35.8:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 50 <= age <= 54:
                if body_fat_rate < 22.3:
                    return 60, "偏瘦"
                elif 22.3 <= body_fat_rate < 31.1:
                    return 100, "正常"
                elif 31.2 <= body_fat_rate < 36.6:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
            elif 55 <= age <= 59:
                if body_fat_rate < 22.6:
                    return 60, "偏瘦"
                elif 22.6 <= body_fat_rate < 31.7:
                    return 100, "正常"
                elif 31.8 <= body_fat_rate < 37.2:
                    return 60, "超重"
                else:
                    return 20, "肥胖"
        
        # 默认返回值
        return 60, "未定义"
    
    def _evaluate_vital_capacity(self, vital_capacity: int, gender: Any, age: int) -> Tuple[float, str]:
        """评估肺活量，按照表2-8男性成年人肺活量评分表和表2-9女性成年人肺活量评分表"""
        # 确定年龄组
        age_group = None
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        
        if gender.value == "男":
            # 男性肺活量评分标准
            # [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            # 每个年龄段对应的肺活量值
            male_standards = [
                # 20-24岁
                [2284, 2473, 2954, 3234, 3452, 3643, 3826, 4023, 4254, 4562, 4783, 5127],
                # 25-29岁
                [2275, 2460, 2933, 3208, 3423, 3612, 3794, 3989, 4219, 4525, 4745, 5089],
                # 30-34岁
                [2199, 2376, 2831, 3097, 3305, 3488, 3664, 3853, 4076, 4375, 4590, 4928],
                # 35-39岁
                [2099, 2271, 2713, 2972, 3174, 3352, 3523, 3708, 3927, 4222, 4434, 4769],
                # 40-44岁
                [1995, 2160, 2588, 2839, 3035, 3208, 3375, 3555, 3769, 4058, 4268, 4600],
                # 45-49岁
                [1896, 2054, 2464, 2705, 2895, 3063, 3224, 3400, 3608, 3891, 4096, 4421],
                # 50-54岁
                [1777, 1927, 2320, 2554, 2739, 2903, 3062, 3235, 3441, 3719, 3921, 4240],
                # 55-59岁
                [1621, 1762, 2138, 2367, 2551, 2716, 2878, 3054, 3261, 3540, 3742, 4059]
            ]
            
            if age_group is not None:
                standards = male_standards[age_group]
                if vital_capacity < standards[0]:
                    return 10, "不合格"
                elif vital_capacity < standards[1]:
                    return 30, "不合格"
                elif vital_capacity < standards[2]:
                    return 50, "合格"
                elif vital_capacity < standards[3]:
                    return 55, "合格"
                elif vital_capacity < standards[4]:
                    return 60, "合格"
                elif vital_capacity < standards[5]:
                    return 65, "良好"
                elif vital_capacity < standards[6]:
                    return 70, "良好"
                elif vital_capacity < standards[7]:
                    return 75, "良好"
                elif vital_capacity < standards[8]:
                    return 80, "良好"
                elif vital_capacity < standards[9]:
                    return 85, "优秀"
                elif vital_capacity < standards[10]:
                    return 90, "优秀"
                elif vital_capacity < standards[11]:
                    return 95, "优秀"
                else:
                    return 100, "优秀"
        else:  # 女性
            # 女性肺活量评分标准
            # [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            # 每个年龄段对应的肺活量值
            female_standards = [
                # 20-24岁
                [1598, 1711, 2010, 2190, 2333, 2461, 2585, 2721, 2887, 3116, 3285, 3559],
                # 25-29岁
                [1555, 1672, 1977, 2160, 2305, 2434, 2560, 2696, 2861, 3086, 3250, 3513],
                # 30-34岁
                [1493, 1611, 1920, 2105, 2250, 2380, 2505, 2642, 2805, 3026, 3187, 3443],
                # 35-39岁
                [1428, 1546, 1854, 2037, 2182, 2311, 2435, 2571, 2732, 2951, 3111, 3365],
                # 40-44岁
                [1364, 1477, 1776, 1954, 2096, 2221, 2343, 2476, 2635, 2853, 3012, 3265],
                # 45-49岁
                [1300, 1407, 1691, 1862, 1998, 2120, 2238, 2368, 2524, 2739, 2897, 3150],
                # 50-54岁
                [1243, 1344, 1615, 1781, 1914, 2033, 2150, 2278, 2433, 2647, 2804, 3057],
                # 55-59岁
                [1151, 1247, 1506, 1667, 1797, 1914, 2031, 2158, 2311, 2520, 2673, 2918]
            ]
            
            if age_group is not None:
                standards = female_standards[age_group]
                if vital_capacity < standards[0]:
                    return 10, "不合格"
                elif vital_capacity < standards[1]:
                    return 30, "不合格"
                elif vital_capacity < standards[2]:
                    return 50, "合格"
                elif vital_capacity < standards[3]:
                    return 55, "合格"
                elif vital_capacity < standards[4]:
                    return 60, "合格"
                elif vital_capacity < standards[5]:
                    return 65, "良好"
                elif vital_capacity < standards[6]:
                    return 70, "良好"
                elif vital_capacity < standards[7]:
                    return 75, "良好"
                elif vital_capacity < standards[8]:
                    return 80, "良好"
                elif vital_capacity < standards[9]:
                    return 85, "优秀"
                elif vital_capacity < standards[10]:
                    return 90, "优秀"
                elif vital_capacity < standards[11]:
                    return 95, "优秀"
                else:
                    return 100, "优秀"
        
        # 默认返回值
        return 60, "未定义"
    
    def _evaluate_max_oxygen_uptake(self, max_oxygen_uptake: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估最大摄氧量（功率车二级负荷试验）"""
        
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [27.5, 29.5, 34.9, 38.3, 41.0, 43.5, 45.9, 48.5, 51.6, 55.9, 59.0, 63.8, 63.9],
                # 25-29岁
                [27.2, 29.0, 34.1, 37.2, 39.8, 42.1, 44.3, 46.8, 50.0, 54.4, 57.7, 63.3, 63.4],
                # 30-34岁
                [25.3, 27.0, 31.6, 34.4, 36.6, 38.6, 40.6, 42.8, 45.5, 49.5, 52.5, 57.6, 57.7],
                # 35-39岁
                [23.9, 25.5, 29.9, 32.6, 34.7, 36.6, 38.5, 40.6, 43.2, 47.0, 50.0, 55, 55.1],
                # 40-44岁
                [22.1, 23.7, 28.2, 31.0, 33.3, 35.3, 37.2, 39.4, 42.2, 46.3, 49.5, 54.8, 54.9],
                # 45-49岁
                [21.3, 22.7, 27.0, 29.6, 31.7, 33.7, 35.6, 37.8, 40.6, 44.6, 47.8, 53.1, 53.2],
                # 50-54岁
                [20.5, 21.7, 25.3, 27.7, 29.6, 31.4, 33.2, 35.2, 37.8, 41.7, 44.7, 50.1, 50.2],
                # 55-59岁
                [19.9, 21.0, 24.4, 26.6, 28.4, 30.2, 31.9, 34.0, 36.6, 40.4, 43.4, 48.7, 48.8]
            ]
            
            standards = male_standards[age_group]
            if max_oxygen_uptake < standards[0]:
                return 10, "不合格"
            elif max_oxygen_uptake <= standards[1]:
                return 30, "不合格"
            elif max_oxygen_uptake <= standards[2]:
                return 50, "合格"
            elif max_oxygen_uptake <= standards[3]:
                return 55, "合格"
            elif max_oxygen_uptake <= standards[4]:
                return 60, "合格"
            elif max_oxygen_uptake <= standards[5]:
                return 65, "良好"
            elif max_oxygen_uptake <= standards[6]:
                return 70, "良好"
            elif max_oxygen_uptake <= standards[7]:
                return 75, "良好"
            elif max_oxygen_uptake <= standards[8]:
                return 80, "良好"
            elif max_oxygen_uptake <= standards[9]:
                return 85, "优秀"
            elif max_oxygen_uptake <= standards[10]:
                return 90, "优秀"
            elif max_oxygen_uptake <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [26.7, 28.9, 34.6, 37.7, 40.0, 41.9, 43.6, 45.6, 48.0, 51.6, 54.3, 58.7, 58.8],
                # 25-29岁
                [26.4, 28.5, 33.9, 36.8, 39.0, 40.8, 42.5, 44.4, 46.9, 50.4, 53.2, 57.9, 58.0],
                # 30-34岁
                [24.7, 26.6, 31.6, 34.3, 36.3, 38.0, 39.5, 41.3, 43.6, 47.0, 49.7, 54.3, 54.4],
                # 35-39岁
                [22.2, 24.0, 28.6, 31.2, 33.0, 34.6, 36.0, 37.7, 39.9, 43.2, 45.8, 50.5, 50.6],
                # 40-44岁
                [20.9, 22.6, 27.2, 29.7, 31.6, 33.1, 34.5, 36.1, 38.3, 41.6, 44.3, 49.1, 49.2],
                # 45-49岁
                [19.8, 21.4, 25.9, 28.3, 30.1, 31.5, 32.8, 34.3, 36.3, 39.5, 42.1, 46.6, 46.7],
                # 50-54岁
                [18.2, 19.7, 23.6, 25.7, 27.1, 28.3, 29.3, 30.6, 32.2, 34.8, 36.8, 40.5, 40.6],
                # 55-59岁
                [16.6, 18.2, 22.3, 24.4, 25.9, 27.0, 28.0, 29.3, 30.9, 33.5, 35.6, 39.2, 39.3]
            ]
            
            standards = female_standards[age_group]
            if max_oxygen_uptake < standards[0]:
                return 10, "不合格"
            elif max_oxygen_uptake <= standards[1]:
                return 30, "不合格"
            elif max_oxygen_uptake <= standards[2]:
                return 50, "合格"
            elif max_oxygen_uptake <= standards[3]:
                return 55, "合格"
            elif max_oxygen_uptake <= standards[4]:
                return 60, "合格"
            elif max_oxygen_uptake <= standards[5]:
                return 65, "良好"
            elif max_oxygen_uptake <= standards[6]:
                return 70, "良好"
            elif max_oxygen_uptake <= standards[7]:
                return 75, "良好"
            elif max_oxygen_uptake <= standards[8]:
                return 80, "良好"
            elif max_oxygen_uptake <= standards[9]:
                return 85, "优秀"
            elif max_oxygen_uptake <= standards[10]:
                return 90, "优秀"
            elif max_oxygen_uptake <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_flexibility(self, sit_and_reach: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估柔韧性（坐位体前屈，20-59岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [-8.9, -6.5, -0.8, 2.2, 4.4, 6.4, 8.3, 10.2, 12.5, 15.5, 17.7, 21.2, 21.3],
                # 25-29岁
                [-10.3, -7.9, -2.2, 0.8, 3.0, 5.0, 6.9, 8.9, 11.1, 14.1, 16.3, 19.8, 19.9],
                # 30-34岁
                [-11.2, -8.8, -3.1, -0.1, 2.2, 4.2, 6.1, 8.0, 10.3, 13.3, 15.5, 19.0, 19.1],
                # 35-39岁
                [-11.5, -9.1, -3.3, -0.3, 1.9, 3.9, 5.8, 7.8, 10.0, 13.0, 15.2, 18.7, 18.8],
                # 40-44岁
                [-11.4, -9.0, -3.3, -0.3, 2.0, 3.9, 5.8, 7.8, 10.1, 13.1, 15.3, 18.8, 18.9],
                # 45-49岁
                [-11.6, -9.2, -3.4, -0.4, 1.8, 3.8, 5.7, 7.7, 9.9, 12.9, 15.1, 18.7, 18.8],
                # 50-54岁
                [-12.1, -9.7, -4.0, -0.9, 1.3, 3.3, 5.2, 7.2, 9.4, 12.4, 14.6, 18.2, 18.3],
                # 55-59岁
                [-13.0, -10.6, -4.8, -1.8, 0.4, 2.4, 4.3, 6.3, 8.6, 11.6, 13.8, 17.3, 17.4]
            ]
            
            standards = male_standards[age_group]
            if sit_and_reach < standards[0]:
                return 10, "不合格"
            elif sit_and_reach <= standards[1]:
                return 30, "不合格"
            elif sit_and_reach <= standards[2]:
                return 50, "合格"
            elif sit_and_reach <= standards[3]:
                return 55, "合格"
            elif sit_and_reach <= standards[4]:
                return 60, "合格"
            elif sit_and_reach <= standards[5]:
                return 65, "良好"
            elif sit_and_reach <= standards[6]:
                return 70, "良好"
            elif sit_and_reach <= standards[7]:
                return 75, "良好"
            elif sit_and_reach <= standards[8]:
                return 80, "良好"
            elif sit_and_reach <= standards[9]:
                return 85, "优秀"
            elif sit_and_reach <= standards[10]:
                return 90, "优秀"
            elif sit_and_reach <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [-4.3, -2.0, 3.4, 6.3, 8.4, 10.3, 12.1, 14.0, 16.1, 19.0, 21.1, 24.4, 24.5],
                # 25-29岁
                [-5.5, -3.2, 2.3, 5.1, 7.3, 9.2, 11.0, 12.9, 15.0, 17.9, 20.0, 23.4, 23.5],
                # 30-34岁
                [-6.5, -4.2, 1.3, 4.2, 6.3, 8.2, 10.0, 11.9, 14.1, 16.9, 19.0, 22.4, 22.5],
                # 35-39岁
                [-7.0, -4.7, 0.8, 3.7, 5.8, 7.7, 9.5, 11.4, 13.6, 16.5, 18.6, 21.9, 22.0],
                # 40-44岁
                [-7.0, -4.7, 0.8, 3.7, 5.9, 7.8, 9.6, 11.5, 13.7, 16.5, 18.6, 22.0, 22.1],
                # 45-49岁
                [-7.0, -4.7, 0.8, 3.7, 5.9, 7.8, 9.7, 11.6, 13.8, 16.7, 18.8, 22.2, 22.3],
                # 50-54岁
                [-7.0, -4.7, 0.9, 3.8, 6.1, 8.0, 9.8, 11.8, 14.0, 16.9, 19.1, 22.5, 22.6],
                # 55-59岁
                [-7.4, -5.0, 0.6, 3.6, 5.9, 7.8, 9.7, 11.6, 13.9, 16.9, 19.0, 22.5, 22.6]
            ]
            
            standards = female_standards[age_group]
            if sit_and_reach < standards[0]:
                return 10, "不合格"
            elif sit_and_reach <= standards[1]:
                return 30, "不合格"
            elif sit_and_reach <= standards[2]:
                return 50, "合格"
            elif sit_and_reach <= standards[3]:
                return 55, "合格"
            elif sit_and_reach <= standards[4]:
                return 60, "合格"
            elif sit_and_reach <= standards[5]:
                return 65, "良好"
            elif sit_and_reach <= standards[6]:
                return 70, "良好"
            elif sit_and_reach <= standards[7]:
                return 75, "良好"
            elif sit_and_reach <= standards[8]:
                return 80, "良好"
            elif sit_and_reach <= standards[9]:
                return 85, "优秀"
            elif sit_and_reach <= standards[10]:
                return 90, "优秀"
            elif sit_and_reach <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_balance(self, single_leg_stand: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估平衡能力（闭眼单脚站立，20-59岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准（表2-22）
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [4, 4, 8, 11, 15, 18, 23, 29, 37, 50, 62, 85, 86],
                # 25-29岁
                [4, 4, 7, 10, 14, 17, 21, 27, 34, 47, 58, 79, 80],
                # 30-34岁
                [4, 4, 7, 10, 13, 16, 20, 25, 32, 44, 55, 75, 76],
                # 35-39岁
                [4, 4, 7, 9, 12, 15, 18, 23, 30, 41, 51, 70, 71],
                # 40-44岁
                [4, 4, 6, 8, 11, 13, 16, 21, 27, 36, 45, 63, 64],
                # 45-49岁
                [3, 3, 5, 7, 9, 11, 14, 17, 22, 31, 38, 54, 55],
                # 50-54岁
                [3, 3, 5, 6, 8, 10, 12, 15, 19, 26, 32, 45, 46],
                # 55-59岁
                [3, 3, 4, 6, 7, 8, 10, 13, 16, 22, 27, 37, 38]
            ]
            
            standards = male_standards[age_group]
            if single_leg_stand < standards[0]:
                return 10, "不合格"
            elif single_leg_stand <= standards[1]:
                return 30, "不合格"
            elif single_leg_stand <= standards[2]:
                return 50, "合格"
            elif single_leg_stand <= standards[3]:
                return 55, "合格"
            elif single_leg_stand <= standards[4]:
                return 60, "合格"
            elif single_leg_stand <= standards[5]:
                return 65, "良好"
            elif single_leg_stand <= standards[6]:
                return 70, "良好"
            elif single_leg_stand <= standards[7]:
                return 75, "良好"
            elif single_leg_stand <= standards[8]:
                return 80, "良好"
            elif single_leg_stand <= standards[9]:
                return 85, "优秀"
            elif single_leg_stand <= standards[10]:
                return 90, "优秀"
            elif single_leg_stand <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准（表2-23）
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [5, 5, 9, 12, 16, 20, 25, 32, 40, 55, 67, 89, 90],
                # 25-29岁
                [5, 5, 8, 12, 15, 19, 24, 30, 39, 52, 64, 86, 87],
                # 30-34岁
                [4, 4, 8, 11, 14, 18, 22, 28, 35, 48, 59, 80, 81],
                # 35-39岁
                [4, 4, 7, 10, 13, 16, 20, 26, 33, 45, 55, 75, 76],
                # 40-44岁
                [4, 4, 6, 9, 12, 15, 19, 23, 30, 41, 51, 71, 72],
                # 45-49岁
                [4, 3, 6, 8, 10, 13, 16, 20, 25, 35, 44, 62, 63],
                # 50-54岁
                [3, 3, 5, 7, 8, 10, 13, 16, 21, 28, 36, 51, 52],
                # 55-59岁
                [3, 3, 4, 5, 7, 8, 10, 13, 16, 22, 28, 39, 40]
            ]
            
            standards = female_standards[age_group]
            if single_leg_stand < standards[0]:
                return 10, "不合格"
            elif single_leg_stand <= standards[1]:
                return 30, "不合格"
            elif single_leg_stand <= standards[2]:
                return 50, "合格"
            elif single_leg_stand <= standards[3]:
                return 55, "合格"
            elif single_leg_stand <= standards[4]:
                return 60, "合格"
            elif single_leg_stand <= standards[5]:
                return 65, "良好"
            elif single_leg_stand <= standards[6]:
                return 70, "良好"
            elif single_leg_stand <= standards[7]:
                return 75, "良好"
            elif single_leg_stand <= standards[8]:
                return 80, "良好"
            elif single_leg_stand <= standards[9]:
                return 85, "优秀"
            elif single_leg_stand <= standards[10]:
                return 90, "优秀"
            elif single_leg_stand <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_reaction_time(self, reaction_time: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估选择反应时间（20-59岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准（表2-24）
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [0.71, 0.70, 0.63, 0.60, 0.57, 0.55, 0.53, 0.51, 0.49, 0.47, 0.45, 0.43, 0.42],
                # 25-29岁
                [0.72, 0.70, 0.64, 0.60, 0.58, 0.56, 0.54, 0.52, 0.50, 0.48, 0.46, 0.44, 0.43],
                # 30-34岁
                [0.73, 0.71, 0.64, 0.61, 0.59, 0.56, 0.55, 0.53, 0.51, 0.48, 0.47, 0.45, 0.44],
                # 35-39岁
                [0.75, 0.72, 0.65, 0.62, 0.59, 0.57, 0.55, 0.53, 0.51, 0.49, 0.47, 0.45, 0.44],
                # 40-44岁
                [0.79, 0.76, 0.68, 0.64, 0.61, 0.59, 0.56, 0.54, 0.52, 0.50, 0.48, 0.46, 0.45],
                # 45-49岁
                [0.82, 0.79, 0.70, 0.66, 0.63, 0.60, 0.58, 0.56, 0.54, 0.51, 0.49, 0.47, 0.46],
                # 50-54岁
                [0.86, 0.82, 0.73, 0.68, 0.65, 0.63, 0.60, 0.58, 0.56, 0.53, 0.51, 0.48, 0.47],
                # 55-59岁
                [0.91, 0.87, 0.76, 0.71, 0.67, 0.64, 0.62, 0.60, 0.57, 0.54, 0.52, 0.49, 0.48]
            ]
            
            standards = male_standards[age_group]
            if reaction_time > standards[0]:
                return 10, "不合格"
            elif reaction_time <= standards[0] and reaction_time > standards[1]:
                return 30, "不合格"
            elif reaction_time <= standards[1] and reaction_time > standards[2]:
                return 50, "合格"
            elif reaction_time <= standards[2] and reaction_time > standards[3]:
                return 55, "合格"
            elif reaction_time <= standards[3] and reaction_time > standards[4]:
                return 60, "合格"
            elif reaction_time <= standards[4] and reaction_time > standards[5]:
                return 65, "良好"
            elif reaction_time <= standards[5] and reaction_time > standards[6]:
                return 70, "良好"
            elif reaction_time <= standards[6] and reaction_time > standards[7]:
                return 75, "良好"
            elif reaction_time <= standards[7] and reaction_time > standards[8]:
                return 80, "良好"
            elif reaction_time <= standards[8] and reaction_time > standards[9]:
                return 85, "优秀"
            elif reaction_time <= standards[9] and reaction_time > standards[10]:
                return 90, "优秀"
            elif reaction_time <= standards[10] and reaction_time > standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准（表2-25）
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [0.75, 0.74, 0.67, 0.63, 0.61, 0.58, 0.56, 0.54, 0.52, 0.50, 0.48, 0.46, 0.45],
                # 25-29岁
                [0.76, 0.74, 0.67, 0.64, 0.61, 0.59, 0.57, 0.55, 0.53, 0.51, 0.49, 0.47, 0.46],
                # 30-34岁
                [0.77, 0.75, 0.68, 0.65, 0.62, 0.60, 0.58, 0.56, 0.54, 0.51, 0.50, 0.47, 0.46],
                # 35-39岁
                [0.80, 0.77, 0.69, 0.66, 0.63, 0.61, 0.59, 0.57, 0.55, 0.52, 0.50, 0.48, 0.47],
                # 40-44岁
                [0.85, 0.81, 0.72, 0.67, 0.64, 0.62, 0.60, 0.58, 0.56, 0.53, 0.51, 0.49, 0.48],
                # 45-49岁
                [0.90, 0.86, 0.75, 0.70, 0.66, 0.64, 0.61, 0.59, 0.57, 0.54, 0.52, 0.50, 0.49],
                # 50-54岁
                [0.94, 0.89, 0.77, 0.71, 0.68, 0.65, 0.63, 0.61, 0.58, 0.55, 0.53, 0.50, 0.49],
                # 55-59岁
                [1.00, 0.94, 0.80, 0.74, 0.70, 0.67, 0.64, 0.62, 0.59, 0.56, 0.54, 0.51, 0.50]
            ]
            
            standards = female_standards[age_group]
            if reaction_time > standards[0]:
                return 10, "不合格"
            elif reaction_time <= standards[0] and reaction_time > standards[1]:
                return 30, "不合格"
            elif reaction_time <= standards[1] and reaction_time > standards[2]:
                return 50, "合格"
            elif reaction_time <= standards[2] and reaction_time > standards[3]:
                return 55, "合格"
            elif reaction_time <= standards[3] and reaction_time > standards[4]:
                return 60, "合格"
            elif reaction_time <= standards[4] and reaction_time > standards[5]:
                return 65, "良好"
            elif reaction_time <= standards[5] and reaction_time > standards[6]:
                return 70, "良好"
            elif reaction_time <= standards[6] and reaction_time > standards[7]:
                return 75, "良好"
            elif reaction_time <= standards[7] and reaction_time > standards[8]:
                return 80, "良好"
            elif reaction_time <= standards[8] and reaction_time > standards[9]:
                return 85, "优秀"
            elif reaction_time <= standards[9] and reaction_time > standards[10]:
                return 90, "优秀"
            elif reaction_time <= standards[10] and reaction_time > standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_grip_strength(self, grip_strength: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估握力"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            # 对于不在20-59岁范围内的，使用简化标准
            if gender.value == "男":
                if grip_strength >= 40:
                    return 85, "良好"
                elif grip_strength >= 30:
                    return 60, "合格"
                else:
                    return 40, "不合格"
            else:
                if grip_strength >= 25:
                    return 85, "良好"
                elif grip_strength >= 15:
                    return 60, "合格"
                else:
                    return 40, "不合格"
        
        # 男性评分标准
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [29.0, 30.7, 35.5, 38.3, 40.4, 42.4, 44.2, 46.2, 48.4, 51.4, 53.5, 56.6, 56.7],
                # 25-29岁
                [29.6, 31.4, 36.2, 39.1, 41.3, 43.2, 45.1, 47.1, 49.4, 52.4, 54.4, 57.6, 57.7],
                # 30-34岁
                [29.9, 31.7, 36.5, 39.3, 41.5, 43.5, 45.4, 47.3, 49.6, 52.5, 54.6, 57.7, 57.8],
                # 35-39岁
                [29.6, 31.4, 36.2, 38.9, 41.1, 43.1, 44.9, 46.9, 49.1, 51.9, 53.9, 56.9, 57.0],
                # 40-44岁
                [29.3, 31.1, 35.8, 38.6, 40.8, 42.7, 44.5, 46.5, 48.6, 51.5, 53.4, 56.3, 56.4],
                # 45-49岁
                [28.9, 30.6, 35.3, 38.0, 40.1, 42.0, 43.8, 45.8, 47.9, 50.7, 52.6, 55.5, 55.6],
                # 50-54岁
                [28.1, 29.7, 34.2, 36.9, 39.0, 40.8, 42.6, 44.5, 46.7, 49.5, 51.4, 54.4, 54.5],
                # 55-59岁
                [26.2, 27.8, 32.3, 35.0, 37.1, 39.0, 40.8, 42.7, 44.9, 47.7, 49.6, 52.6, 52.7]
            ]
            
            standards = male_standards[age_group]
            if grip_strength < standards[0]:
                return 10, "不合格"
            elif grip_strength <= standards[1]:
                return 30, "不合格"
            elif grip_strength <= standards[2]:
                return 50, "合格"
            elif grip_strength <= standards[3]:
                return 55, "合格"
            elif grip_strength <= standards[4]:
                return 60, "合格"
            elif grip_strength <= standards[5]:
                return 65, "良好"
            elif grip_strength <= standards[6]:
                return 70, "良好"
            elif grip_strength <= standards[7]:
                return 75, "良好"
            elif grip_strength <= standards[8]:
                return 80, "良好"
            elif grip_strength <= standards[9]:
                return 85, "优秀"
            elif grip_strength <= standards[10]:
                return 90, "优秀"
            elif grip_strength <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [17.3, 18.3, 21.1, 22.9, 24.3, 25.6, 26.9, 28.3, 29.9, 32.0, 33.4, 35.7, 35.8],
                # 25-29岁
                [17.3, 18.3, 21.2, 22.9, 24.3, 25.6, 26.9, 28.2, 29.8, 31.9, 33.3, 35.5, 35.6],
                # 30-34岁
                [17.5, 18.6, 21.5, 23.3, 24.7, 26.0, 27.3, 28.6, 30.2, 32.2, 33.7, 35.9, 36.0],
                # 35-39岁
                [17.6, 18.6, 21.7, 23.5, 24.9, 26.2, 27.5, 28.8, 30.4, 32.4, 33.8, 35.9, 36.0],
                # 40-44岁
                [17.6, 18.7, 21.8, 23.7, 25.1, 26.4, 27.7, 29.0, 30.5, 32.5, 33.9, 36.1, 36.2],
                # 45-49岁
                [17.4, 18.5, 21.5, 23.3, 24.7, 26.0, 27.3, 28.6, 30.1, 32.1, 33.5, 35.7, 35.8],
                # 50-54岁
                [16.8, 17.8, 20.7, 22.4, 23.8, 25.1, 26.3, 27.6, 29.1, 31.1, 32.5, 34.8, 34.9],
                # 55-59岁
                [16.0, 17.1, 20.0, 21.8, 23.2, 24.4, 25.6, 26.9, 28.4, 30.5, 31.9, 34.1, 34.2]
            ]
            
            standards = female_standards[age_group]
            if grip_strength < standards[0]:
                return 10, "不合格"
            elif grip_strength <= standards[1]:
                return 30, "不合格"
            elif grip_strength <= standards[2]:
                return 50, "合格"
            elif grip_strength <= standards[3]:
                return 55, "合格"
            elif grip_strength <= standards[4]:
                return 60, "合格"
            elif grip_strength <= standards[5]:
                return 65, "良好"
            elif grip_strength <= standards[6]:
                return 70, "良好"
            elif grip_strength <= standards[7]:
                return 75, "良好"
            elif grip_strength <= standards[8]:
                return 80, "良好"
            elif grip_strength <= standards[9]:
                return 85, "优秀"
            elif grip_strength <= standards[10]:
                return 90, "优秀"
            elif grip_strength <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_sit_ups(self, sit_ups_per_minute: int, gender: Any, age: int) -> Tuple[float, str]:
        """评估一分钟仰卧起坐（20-59岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [10, 11, 17, 20, 22, 25, 27, 29, 32, 35, 38, 42, 43],
                # 25-29岁
                [10, 11, 16, 19, 21, 23, 25, 27, 30, 33, 36, 40, 41],
                # 30-34岁
                [9, 10, 15, 18, 20, 22, 24, 26, 28, 32, 34, 38, 39],
                # 35-39岁
                [8, 9, 14, 17, 19, 21, 23, 25, 27, 30, 32, 36, 37],
                # 40-44岁
                [8, 8, 13, 15, 17, 19, 21, 23, 25, 28, 31, 34, 35],
                # 45-49岁
                [6, 7, 11, 14, 16, 17, 19, 21, 23, 26, 28, 32, 33],
                # 50-54岁
                [5, 6, 10, 12, 14, 15, 17, 19, 21, 24, 26, 29, 30],
                # 55-59岁
                [4, 4, 8, 10, 12, 14, 15, 17, 19, 22, 24, 27, 28]
            ]
            
            standards = male_standards[age_group]
            if sit_ups_per_minute < standards[0]:
                return 10, "不合格"
            elif sit_ups_per_minute <= standards[1]:
                return 30, "不合格"
            elif sit_ups_per_minute <= standards[2]:
                return 50, "合格"
            elif sit_ups_per_minute <= standards[3]:
                return 55, "合格"
            elif sit_ups_per_minute <= standards[4]:
                return 60, "合格"
            elif sit_ups_per_minute <= standards[5]:
                return 65, "良好"
            elif sit_ups_per_minute <= standards[6]:
                return 70, "良好"
            elif sit_ups_per_minute <= standards[7]:
                return 75, "良好"
            elif sit_ups_per_minute <= standards[8]:
                return 80, "良好"
            elif sit_ups_per_minute <= standards[9]:
                return 85, "优秀"
            elif sit_ups_per_minute <= standards[10]:
                return 90, "优秀"
            elif sit_ups_per_minute <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [7, 8, 13, 16, 18, 20, 22, 24, 27, 30, 33, 36, 37],
                # 25-29岁
                [6, 7, 11, 14, 16, 18, 20, 22, 24, 27, 29, 32, 33],
                # 30-34岁
                [5, 6, 10, 12, 14, 16, 18, 20, 22, 25, 28, 31, 32],
                # 35-39岁
                [5, 5, 9, 12, 14, 16, 18, 20, 22, 25, 27, 30, 31],
                # 40-44岁
                [4, 5, 8, 11, 13, 15, 17, 19, 21, 24, 26, 29, 30],
                # 45-49岁
                [3, 4, 7, 9, 11, 13, 15, 17, 19, 22, 24, 27, 28],
                # 50-54岁
                [3, 3, 5, 7, 9, 11, 13, 15, 17, 20, 22, 25, 26],
                # 55-59岁
                [2, 2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 23, 24]
            ]
            
            standards = female_standards[age_group]
            if sit_ups_per_minute < standards[0]:
                return 10, "不合格"
            elif sit_ups_per_minute <= standards[1]:
                return 30, "不合格"
            elif sit_ups_per_minute <= standards[2]:
                return 50, "合格"
            elif sit_ups_per_minute <= standards[3]:
                return 55, "合格"
            elif sit_ups_per_minute <= standards[4]:
                return 60, "合格"
            elif sit_ups_per_minute <= standards[5]:
                return 65, "良好"
            elif sit_ups_per_minute <= standards[6]:
                return 70, "良好"
            elif sit_ups_per_minute <= standards[7]:
                return 75, "良好"
            elif sit_ups_per_minute <= standards[8]:
                return 80, "良好"
            elif sit_ups_per_minute <= standards[9]:
                return 85, "优秀"
            elif sit_ups_per_minute <= standards[10]:
                return 90, "优秀"
            elif sit_ups_per_minute <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_push_ups(self, push_ups: int, gender: Any, age: int) -> Tuple[float, str]:
        """评估俯卧撑/跪卧撑（20-59岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        elif 50 <= age <= 54:
            age_group = 6
        elif 55 <= age <= 59:
            age_group = 7
        else:
            return 60, "未定义"
        
        # 男性评分标准（俯卧撑）
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [5, 6, 11, 14, 17, 20, 22, 25, 29, 34, 38, 44, 45],
                # 25-29岁
                [5, 5, 10, 13, 16, 18, 21, 24, 27, 32, 36, 41, 42],
                # 30-34岁
                [5, 5, 9, 12, 15, 17, 20, 22, 26, 30, 34, 39, 40],
                # 35-39岁
                [5, 5, 9, 12, 14, 16, 19, 21, 25, 29, 33, 38, 39],
                # 40-44岁
                [4, 4, 8, 11, 13, 15, 18, 20, 23, 28, 31, 37, 38],
                # 45-49岁
                [4, 4, 7, 10, 12, 14, 16, 19, 22, 26, 29, 34, 35],
                # 50-54岁
                [3, 3, 6, 8, 10, 12, 14, 17, 19, 23, 26, 31, 32],
                # 55-59岁
                [3, 3, 5, 7, 9, 11, 13, 15, 17, 21, 24, 28, 29]
            ]
            
            standards = male_standards[age_group]
            if push_ups < standards[0]:
                return 10, "不合格"
            elif push_ups <= standards[1]:
                return 30, "不合格"
            elif push_ups <= standards[2]:
                return 50, "合格"
            elif push_ups <= standards[3]:
                return 55, "合格"
            elif push_ups <= standards[4]:
                return 60, "合格"
            elif push_ups <= standards[5]:
                return 65, "良好"
            elif push_ups <= standards[6]:
                return 70, "良好"
            elif push_ups <= standards[7]:
                return 75, "良好"
            elif push_ups <= standards[8]:
                return 80, "良好"
            elif push_ups <= standards[9]:
                return 85, "优秀"
            elif push_ups <= standards[10]:
                return 90, "优秀"
            elif push_ups <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准（跪卧撑）
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [3, 3, 7, 10, 12, 15, 18, 20, 24, 28, 32, 37, 38],
                # 25-29岁
                [3, 3, 7, 10, 12, 15, 17, 20, 23, 28, 31, 36, 37],
                # 30-34岁
                [3, 3, 7, 10, 12, 15, 17, 20, 23, 28, 31, 36, 37],
                # 35-39岁
                [3, 3, 7, 10, 12, 15, 17, 20, 23, 28, 31, 36, 37],
                # 40-44岁
                [3, 3, 7, 9, 12, 14, 17, 20, 23, 28, 31, 36, 37],
                # 45-49岁
                [3, 3, 6, 9, 11, 14, 16, 19, 23, 27, 31, 36, 37],
                # 50-54岁
                [2, 2, 5, 8, 10, 12, 15, 18, 21, 26, 29, 35, 36],
                # 55-59岁
                [2, 2, 5, 7, 9, 11, 13, 16, 19, 24, 27, 33, 34]
            ]
            
            standards = female_standards[age_group]
            if push_ups < standards[0]:
                return 10, "不合格"
            elif push_ups <= standards[1]:
                return 30, "不合格"
            elif push_ups <= standards[2]:
                return 50, "合格"
            elif push_ups <= standards[3]:
                return 55, "合格"
            elif push_ups <= standards[4]:
                return 60, "合格"
            elif push_ups <= standards[5]:
                return 65, "良好"
            elif push_ups <= standards[6]:
                return 70, "良好"
            elif push_ups <= standards[7]:
                return 75, "良好"
            elif push_ups <= standards[8]:
                return 80, "良好"
            elif push_ups <= standards[9]:
                return 85, "优秀"
            elif push_ups <= standards[10]:
                return 90, "优秀"
            elif push_ups <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_vertical_jump(self, vertical_jump: float, gender: Any, age: int) -> Tuple[float, str]:
        """评估纵跳高度（20-49岁）"""
        # 年龄段映射 (20-24, 25-29, 30-34, 35-39, 40-44, 45-49)
        if 20 <= age <= 24:
            age_group = 0
        elif 25 <= age <= 29:
            age_group = 1
        elif 30 <= age <= 34:
            age_group = 2
        elif 35 <= age <= 39:
            age_group = 3
        elif 40 <= age <= 44:
            age_group = 4
        elif 45 <= age <= 49:
            age_group = 5
        else:
            return 60, "未定义"
        
        # 男性评分标准
        if gender.value == "男":
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            male_standards = [
                # 20-24岁
                [22.5, 23.9, 28.3, 31.1, 33.4, 35.6, 37.8, 40.2, 42.9, 46.4, 48.9, 52.8, 52.9],
                # 25-29岁
                [22.1, 23.5, 27.7, 30.3, 32.5, 34.5, 36.5, 38.6, 41.1, 44.4, 46.8, 50.5, 50.6],
                # 30-34岁
                [21.5, 22.9, 26.9, 29.3, 31.3, 33.1, 34.9, 36.9, 39.1, 42.2, 44.5, 48.0, 48.1],
                # 35-39岁
                [20.4, 21.7, 25.5, 27.9, 29.8, 31.5, 33.1, 35.0, 37.1, 40.1, 42.2, 45.7, 45.8],
                # 40-44岁
                [18.7, 19.9, 23.6, 25.9, 27.8, 29.5, 31.1, 32.9, 35.1, 38.0, 40.2, 43.6, 43.7],
                # 45-49岁
                [17.2, 18.4, 22.0, 24.2, 26.0, 27.6, 29.2, 30.9, 33.0, 35.9, 38.0, 41.4, 41.5]
            ]
            
            standards = male_standards[age_group]
            if vertical_jump < standards[0]:
                return 10, "不合格"
            elif vertical_jump <= standards[1]:
                return 30, "不合格"
            elif vertical_jump <= standards[2]:
                return 50, "合格"
            elif vertical_jump <= standards[3]:
                return 55, "合格"
            elif vertical_jump <= standards[4]:
                return 60, "合格"
            elif vertical_jump <= standards[5]:
                return 65, "良好"
            elif vertical_jump <= standards[6]:
                return 70, "良好"
            elif vertical_jump <= standards[7]:
                return 75, "良好"
            elif vertical_jump <= standards[8]:
                return 80, "良好"
            elif vertical_jump <= standards[9]:
                return 85, "优秀"
            elif vertical_jump <= standards[10]:
                return 90, "优秀"
            elif vertical_jump <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
        # 女性评分标准
        else:
            # 各年龄段的评分标准 [10分, 30分, 50分, 55分, 60分, 65分, 70分, 75分, 80分, 85分, 90分, 95分, 100分]
            female_standards = [
                # 20-24岁
                [15.9, 16.7, 19.4, 21.1, 22.5, 23.8, 25.1, 26.5, 28.3, 30.7, 32.5, 35.4, 35.5],
                # 25-29岁
                [15.3, 16.1, 18.6, 20.2, 21.5, 22.7, 24.0, 25.3, 26.9, 29.2, 30.9, 33.6, 33.7],
                # 30-34岁
                [14.7, 15.5, 18.0, 19.5, 20.7, 21.9, 23.0, 24.3, 25.8, 28.0, 29.6, 32.3, 32.4],
                # 35-39岁
                [14.1, 14.9, 17.3, 18.8, 20.0, 21.1, 22.2, 23.5, 25.0, 27.0, 28.6, 31.2, 31.3],
                # 40-44岁
                [13.3, 14.1, 16.5, 18.0, 19.2, 20.3, 21.4, 22.5, 24.0, 26.0, 27.5, 29.9, 30.0],
                # 45-49岁
                [12.5, 13.3, 15.6, 17.1, 18.2, 19.3, 20.3, 21.5, 22.9, 24.9, 26.4, 28.8, 28.9]
            ]
            
            standards = female_standards[age_group]
            if vertical_jump < standards[0]:
                return 10, "不合格"
            elif vertical_jump <= standards[1]:
                return 30, "不合格"
            elif vertical_jump <= standards[2]:
                return 50, "合格"
            elif vertical_jump <= standards[3]:
                return 55, "合格"
            elif vertical_jump <= standards[4]:
                return 60, "合格"
            elif vertical_jump <= standards[5]:
                return 65, "良好"
            elif vertical_jump <= standards[6]:
                return 70, "良好"
            elif vertical_jump <= standards[7]:
                return 75, "良好"
            elif vertical_jump <= standards[8]:
                return 80, "良好"
            elif vertical_jump <= standards[9]:
                return 85, "优秀"
            elif vertical_jump <= standards[10]:
                return 90, "优秀"
            elif vertical_jump <= standards[11]:
                return 95, "优秀"
            else:
                return 100, "优秀"
    
    def _evaluate_high_knees(self, high_knees_2min: int, gender: Any) -> Tuple[float, str]:
        """评估2分钟原地高抬腿（老年人）"""
        if gender.value == "男":
            if high_knees_2min >= 180:
                return 95, "优秀"
            elif high_knees_2min >= 150:
                return 85, "良好"
            elif high_knees_2min >= 120:
                return 70, "合格"
            else:
                return 50, "不合格"
        else:  # 女性
            if high_knees_2min >= 160:
                return 95, "优秀"
            elif high_knees_2min >= 130:
                return 85, "良好"
            elif high_knees_2min >= 100:
                return 70, "合格"
            else:
                return 50, "不合格"
    
    def _evaluate_sit_to_stand(self, sit_to_stand_30s: int, gender: Any) -> Tuple[float, str]:
        """评估30秒坐站（老年人）"""
        if gender.value == "男":
            if sit_to_stand_30s >= 25:
                return 95, "优秀"
            elif sit_to_stand_30s >= 20:
                return 85, "良好"
            elif sit_to_stand_30s >= 15:
                return 70, "合格"
            else:
                return 50, "不合格"
        else:  # 女性
            if sit_to_stand_30s >= 22:
                return 95, "优秀"
            elif sit_to_stand_30s >= 18:
                return 85, "良好"
            elif sit_to_stand_30s >= 13:
                return 70, "合格"
            else:
                return 50, "不合格"
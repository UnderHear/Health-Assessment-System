import os
import re
import json
import random
import markdown
from bs4 import BeautifulSoup
from collections import defaultdict, Counter

# 配置参数
MARKDOWN_FOLDER = "ACSM指南markdown_output"
OUTPUT_FILE = "instruction_response_pairs_improved.json"

# 定义不同类型任务的模板
TASK_TEMPLATES = {
    "知识问答": {
        "指令模板": [
            "请解释什么是{术语}？",
            "请说明{术语}在运动处方中的意义？",
            "请简述{术语}的定义及其临床意义。",
            "{术语}的正常值范围是多少？有什么临床意义？"
        ],
        "响应构建": "从文本中提取相关定义、正常值范围和临床意义进行组织。"
    },
    "场景化处方设计": {
        "指令模板": [
            "为一名{年龄}岁、{身体状况}的{性别}{职业}设计一个为期{时长}的{强度}运动处方。请遵循FITT-VP原则。",
            "针对{人群特征}的患者，如何设计个性化的运动处方？请考虑FITT-VP原则。",
            "根据ACSM指南，为{具体情况}的个体制定一份详细的运动计划。"
        ],
        "响应构建": "综合书中关于健康成年人、运动频率、强度、时间、类型、总量与进展的章节，生成符合ACSM指南的个性化方案。"
    },
    "风险评估与禁忌症识别": {
        "指令模板": [
            "{疾病}患者在开始{运动类型}前，需要进行哪些风险筛查？",
            "请列出{人群}进行{运动类型}时的禁忌症。",
            "对于患有{疾病}的个体，运动前应进行哪些健康评估？"
        ],
        "响应构建": "整合'运动前健康筛査'和相关疾病章节内容，列出关键筛查步骤和注意事项。"
    },
    "数据解读与推理": {
        "指令模板": [
            "根据{测试方案}测试结果，某受试者在{测试阶段}达到{测试指标}，请推断其{功能水平}。",
            "分析以下测试数据：{数据}，并给出相应的运动建议。",
            "如何解读{测试类型}的测试结果？请给出具体的评估标准。"
        ],
        "响应构建": "基于书中提供的测试方案标准与解读指南，进行逻辑推理和结论陈述。"
    }
}

# 示例数据，用于填充模板
EXAMPLE_DATA = {
    "术语": ["VO₂max", "心率储备", "最大心率", "体适能", "肌耐力", "柔韧性", "平衡能力", "代谢当量", "运动处方", "FITT-VP原则", "静息心率", "血压", "BMI", "身体成分"],
    "年龄": ["25", "35", "45", "55", "65", "75"],
    "身体状况": ["久坐", "轻度活动", "中度活动", "经常锻炼", "肥胖", "超重", "正常体重"],
    "性别": ["男性", "女性"],
    "职业": ["办公室职员", "教师", "工人", "医生", "护士", "销售人员"],
    "时长": ["4周", "8周", "12周", "24周"],
    "强度": ["初级", "中级", "高级"],
    "人群特征": ["高血压", "糖尿病", "冠心病", "肥胖", "骨质疏松", "关节炎"],
    "具体情况": ["40岁男性、轻度高血压且久坐不动", "60岁女性、2型糖尿病且有轻度关节问题", "50岁男性、肥胖且有心血管疾病家族史"],
    "疾病": ["高血压", "糖尿病", "冠心病", "哮喘", "骨质疏松", "关节炎"],
    "运动类型": ["有氧运动", "抗阻训练", "高强度间歇训练", "柔韧性训练"],
    "人群": ["老年人", "孕妇", "肥胖者", "心血管疾病患者", "糖尿病患者"],
    "测试方案": ["Bruce方案", "Naughton方案", "Balke方案", "YMCA方案"],
    "测试阶段": ["第一阶段结束时", "第二阶段结束时", "第三阶段结束时", "第四阶段结束时"],
    "测试指标": ["最大心率175次/分", "最大摄氧量35ml/kg/min", "运动时间10分钟", "血压达到180/110mmHg"],
    "功能水平": ["心肺功能水平", "运动能力", "健康状况", "体力活动水平"],
    "数据": ["最大心率160次/分，血压140/90mmHg", "BMI 30，腰围100cm", "VO₂max 30ml/kg/min，静息心率75次/分"],
    "测试类型": ["心肺运动测试", "体适能测试", "肌力测试", "柔韧性测试"]
}

class ImprovedInstructionResponseGenerator:
    def __init__(self, markdown_folder, output_file):
        self.markdown_folder = markdown_folder
        self.output_file = output_file
        self.all_text = ""
        self.knowledge_base = {}
        self.section_content_map = defaultdict(list)
        self.instruction_response_pairs = []
        
        # 预定义的关键知识点，从ACSM指南中提取
        self.key_knowledge = {
            "VO₂max": "最大摄氧量（VO₂max）是指人体在极量运动时每分钟每公斤体重所能摄取的最大氧气量，是评估心肺功能的金标准。正常值范围因年龄、性别和体能水平而异，一般健康成年男性约为35-45 ml/kg/min，女性约为27-38 ml/kg/min。在运动处方中，VO₂max可用于确定运动强度、评估训练效果和预测运动风险。",
            "心率储备": "心率储备（HRR）是指最大心率与静息心率之间的差值。计算公式为：心率储备 = 最大心率 - 静息心率。在运动处方中，心率储备常用于确定运动强度，通常建议运动心率保持在储备心率的40%-85%之间，结合FITT原则制定个性化运动方案。",
            "最大心率": "最大心率（HRmax）是指人体在运动过程中所能达到的最快心率。常用的估算公式为：最大心率 = 220 - 年龄。然而，ACSM最新指南建议使用更准确的公式：最大心率 = 208 - 0.7 × 年龄。在运动处方中，最大心率用于确定运动强度区间，通常以最大心率的百分比来表示运动强度。",
            "FITT-VP原则": "FITT-VP原则是制定运动处方的核心原则，包括：频率（Frequency）、强度（Intensity）、时间（Time）、类型（Type）、总量（Volume）和进展（Progression）。ACSM建议健康成年人每周至少进行150分钟中等强度有氧运动或75分钟高强度有氧运动，或等效的组合。同时每周至少进行2天的肌肉力量训练。运动处方应根据个体的健康状况、体能水平和运动目标进行个性化调整。",
            "高血压患者运动处方": "高血压患者的运动处方应遵循FITT-VP原则，以中等强度有氧运动为主，如快走、慢跑、骑自行车等。建议每周进行3-5天，每次30-60分钟的有氧运动，运动强度控制在最大心率的40%-60%或RPE 11-13（稍累至累）。抗阻训练可每周进行2-3天，采用低至中等强度，避免憋气动作。运动前应进行充分热身，运动过程中密切监测血压变化。",
            "糖尿病患者运动处方": "糖尿病患者的运动处方应结合血糖控制目标和并发症情况。建议每周进行5天中等强度有氧运动，每次至少30分钟，或每周3天高强度有氧运动，每次20分钟。同时每周进行2-3天的抗阻训练。运动时间应避开胰岛素作用高峰，避免空腹运动，运动前后监测血糖。伴有并发症的患者应在医生指导下进行运动。",
            "冠心病患者运动处方": "冠心病患者的运动处方需在医疗监督下制定，以有氧耐力训练为基础，结合柔韧性和力量训练。建议每周进行3-5天，每次20-60分钟的有氧运动，运动强度控制在最大心率的40%-80%或RPE 11-14。运动前应进行充分的热身和准备活动，运动过程中密切监测心率和症状，避免高强度和爆发性运动。",
            "Bruce方案": "Bruce方案是一种常用的分级运动试验方案，通过逐步增加跑台的速度和坡度来评估心肺功能。该方案共分为7个阶段，每个阶段持续3分钟。Bruce方案主要用于评估冠心病患者的运动能力和心脏功能，也可用于健康人群的体能评估。测试结果可用于确定运动强度和制定运动处方。"
        }
        
    def load_markdown_files(self):
        """加载所有markdown文件并提取文本内容"""
        print(f"正在加载markdown文件，文件夹：{self.markdown_folder}")
        
        # 获取文件夹中的所有md文件
        md_files = [f for f in os.listdir(self.markdown_folder) if f.endswith('.md')]
        total_files = len(md_files)
        
        for i, md_file in enumerate(md_files):
            file_path = os.path.join(self.markdown_folder, md_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取纯文本内容（去除Markdown格式）
                    text = self.extract_plain_text(content)
                    self.all_text += text + "\n"
                    
                    # 提取章节标题和内容
                    self.extract_sections(content, md_file)
                    
                if (i + 1) % 50 == 0:
                    print(f"已加载 {i + 1}/{total_files} 个文件")
            except Exception as e:
                print(f"加载文件 {md_file} 时出错: {e}")
        
        print(f"共加载 {total_files} 个文件")
        
    def extract_plain_text(self, markdown_content):
        """从Markdown内容中提取纯文本"""
        # 将Markdown转换为HTML
        html = markdown.markdown(markdown_content)
        # 使用BeautifulSoup提取纯文本
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        # 去除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def extract_sections(self, markdown_content, file_name):
        """提取Markdown中的章节标题和内容"""
        # 使用正则表达式提取各级标题和内容
        lines = markdown_content.split('\n')
        current_section = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是标题行
            title_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if title_match:
                # 如果已有当前章节，保存它
                if current_section and current_content:
                    self.section_content_map[current_section].append('\n'.join(current_content))
                    current_content = []
                
                # 设置新的当前章节
                level = len(title_match.group(1))
                title = title_match.group(2)
                current_section = f"{'#' * level} {title}" if level > 1 else title
            else:
                # 添加内容到当前章节
                current_content.append(line)
                
        # 保存最后一个章节
        if current_section and current_content:
            self.section_content_map[current_section].append('\n'.join(current_content))
    
    def build_knowledge_base(self):
        """构建知识库，整合预定义知识和从文档中提取的知识"""
        # 首先添加预定义的关键知识点
        for key, value in self.key_knowledge.items():
            self.knowledge_base[key] = value
            
        # 从文档内容中提取相关知识
        # 例如，提取关于运动处方、风险评估、测试方案等方面的信息
        # 这里简化处理，实际应用中可以使用更复杂的NLP技术
        
        # 提取FITT相关信息
        if "FITT" in self.all_text:
            fit_patterns = [
                r'FITT.*?原则',
                r'频率.*?强度.*?时间.*?类型',
                r'Frequency.*?Intensity.*?Time.*?Type'
            ]
            
            for pattern in fit_patterns:
                matches = re.findall(pattern, self.all_text, re.DOTALL | re.IGNORECASE)
                if matches:
                    self.knowledge_base["FITT原则详情"] = matches[0]
                    break
        
        # 提取运动测试相关信息
        test_patterns = [
            r'Bruce方案.*?阶段',
            r'运动测试.*?步骤',
            r'心肺运动测试.*?评估'
        ]
        
        for pattern in test_patterns:
            matches = re.findall(pattern, self.all_text, re.DOTALL | re.IGNORECASE)
            if matches:
                self.knowledge_base["运动测试信息"] = matches[0]
                break
        
        print(f"知识库构建完成，包含 {len(self.knowledge_base)} 个关键知识点")
        
    def generate_pairs(self, num_pairs=2000):
        """生成指令-响应对"""
        print(f"开始生成指令-响应对，目标数量：{num_pairs}")
        
        task_types = list(TASK_TEMPLATES.keys())
        generated_count = 0
        
        while generated_count < num_pairs:
            # 随机选择任务类型
            task_type = random.choice(task_types)
            templates = TASK_TEMPLATES[task_type]["指令模板"]
            
            # 随机选择一个模板
            template = random.choice(templates)
            
            try:
                # 填充模板
                filled_instruction = self.fill_template(template)
                
                # 生成响应（从知识库中提取相关内容）
                response = self.generate_response(filled_instruction, task_type)
                
                # 添加到结果列表
                self.instruction_response_pairs.append({
                    "instruction": filled_instruction,
                    "response": response,
                    "task_type": task_type
                })
                
                generated_count += 1
                if generated_count % 200 == 0:
                    print(f"已生成 {generated_count}/{num_pairs} 个指令-响应对")
            except Exception as e:
                # 如果填充模板失败，继续尝试
                continue
        
        print(f"指令-响应对生成完成，共生成 {generated_count} 个")
        
    def fill_template(self, template):
        """填充指令模板中的占位符"""
        filled_template = template
        
        # 查找模板中的所有占位符
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        for placeholder in placeholders:
            if placeholder in EXAMPLE_DATA and EXAMPLE_DATA[placeholder]:
                # 随机选择一个示例值
                value = random.choice(EXAMPLE_DATA[placeholder])
                # 替换占位符
                filled_template = filled_template.replace(f"{{{placeholder}}}", value)
            else:
                # 如果没有找到对应的示例数据，使用默认值
                filled_template = filled_template.replace(f"{{{placeholder}}}", "[示例数据]")
                
        return filled_template
        
    def generate_response(self, instruction, task_type):
        """根据指令和任务类型生成响应"""
        # 从指令中提取关键词
        keywords = self.extract_keywords(instruction)
        
        # 根据任务类型和关键词生成响应
        if task_type == "知识问答":
            response = self.generate_knowledge_response(keywords)
        elif task_type == "场景化处方设计":
            response = self.generate_prescription_response(keywords, instruction)
        elif task_type == "风险评估与禁忌症识别":
            response = self.generate_risk_response(keywords, instruction)
        elif task_type == "数据解读与推理":
            response = self.generate_interpretation_response(keywords, instruction)
        else:
            # 默认响应
            response = "根据ACSM运动测试与运动处方指南(第十版)，..."
        
        return response
        
    def extract_keywords(self, instruction):
        """从指令中提取关键词"""
        keywords = []
        
        # 检查指令中是否包含知识库中的关键词
        for key in self.knowledge_base.keys():
            if key in instruction:
                keywords.append(key)
                
        # 检查指令中是否包含预定义的术语
        for term in EXAMPLE_DATA["术语"]:
            if term in instruction and term not in keywords:
                keywords.append(term)
                
        # 检查指令中是否包含疾病名称
        for disease in EXAMPLE_DATA["疾病"] + EXAMPLE_DATA["人群特征"]:
            if disease in instruction and disease not in keywords:
                keywords.append(disease)
                
        return keywords
        
    def generate_knowledge_response(self, keywords):
        """生成知识问答类型的响应"""
        response = ""
        
        # 从知识库中查找相关内容
        for keyword in keywords:
            if keyword in self.knowledge_base:
                response += self.knowledge_base[keyword] + "\n\n"
        
        # 如果没有找到相关内容，使用通用模板
        if not response:
            response = "根据ACSM运动测试与运动处方指南(第十版)，该术语是评估人体运动能力和健康状况的重要指标。在运动处方制定中，了解该术语的定义和临床意义有助于设计科学、安全、有效的运动方案，促进个体健康水平的提高和疾病的预防。"
        
        return response.strip()
        
    def generate_prescription_response(self, keywords, instruction):
        """生成场景化处方设计类型的响应"""
        # 检查是否包含特定疾病的运动处方
        for disease in EXAMPLE_DATA["疾病"] + EXAMPLE_DATA["人群特征"]:
            if disease in instruction and f"{disease}患者运动处方" in self.knowledge_base:
                return self.knowledge_base[f"{disease}患者运动处方"]
        
        # 检查是否包含FITT原则
        if "FITT" in keywords or "运动处方" in keywords:
            if "FITT-VP原则" in self.knowledge_base:
                return self.knowledge_base["FITT-VP原则"]
        
        # 通用运动处方模板
        response = "根据ACSM指南和FITT-VP原则，为该个体设计的运动处方如下：\n"
        response += "1. 频率(Frequency)：每周进行3-5天中等强度有氧运动，2-3天力量训练。\n"
        response += "2. 强度(Intensity)：有氧运动强度控制在最大心率的50%-70%或RPE 11-13（稍累至累）；力量训练采用能完成10-15次重复的重量。\n"
        response += "3. 时间(Time)：每次有氧运动持续30-60分钟，力量训练每个肌群练习2-3组，每组8-12次。\n"
        response += "4. 类型(Type)：有氧运动选择快走、慢跑、游泳、骑自行车等；力量训练包括主要肌群的练习。\n"
        response += "5. 总量(Volume)：每周累计运动时间至少150分钟中等强度有氧运动。\n"
        response += "6. 进展(Progression)：根据个体适应情况，逐渐增加运动时间、频率或强度，每1-2周增加5%-10%。\n"
        response += "7. 注意事项：运动前进行5-10分钟热身，运动后进行5-10分钟放松；运动过程中注意监测身体反应，如有不适及时停止并咨询专业人士。"
        
        return response
        
    def generate_risk_response(self, keywords, instruction):
        """生成风险评估与禁忌症识别类型的响应"""
        response = "在开始运动前，建议进行以下风险筛查和评估：\n"
        response += "1. 健康史评估：详细了解病史、家族史、用药情况和症状，特别关注胸痛、呼吸困难、头晕、晕厥等心血管症状。\n"
        response += "2. 体格检查：测量身高、体重、BMI、血压、心率等基本指标，评估心肺功能和运动能力。\n"
        response += "3. 运动禁忌症识别：包括急性心肌梗死、不稳定性心绞痛、未控制的心力衰竭、严重心律失常、未控制的高血压（收缩压>180mmHg或舒张压>110mmHg）等。\n"
        response += "4. 运动前测试：根据个体情况，可能需要进行心电图、运动负荷试验等检查。\n"
        response += "5. 注意事项：运动过程中应密切监测身体反应，避免高强度和爆发性运动；如有不适，应立即停止并寻求医疗帮助。\n"
        
        # 根据特定疾病添加额外注意事项
        for disease in EXAMPLE_DATA["疾病"]:
            if disease in instruction:
                if disease == "高血压":
                    response += "6. 高血压患者额外注意事项：避免憋气动作和高强度抗阻训练；运动前后监测血压；避免在血压未控制时进行运动。\n"
                elif disease == "糖尿病":
                    response += "6. 糖尿病患者额外注意事项：避免空腹运动；运动时间避开胰岛素作用高峰；运动前后监测血糖；携带糖块以备低血糖时使用。\n"
                elif disease == "冠心病":
                    response += "6. 冠心病患者额外注意事项：在医疗监督下进行运动；避免高强度运动；运动前充分热身；随身携带急救药物。\n"
        
        return response.strip()
        
    def generate_interpretation_response(self, keywords, instruction):
        """生成数据解读与推理类型的响应"""
        # 检查是否包含特定测试方案
        for test in ["Bruce方案", "Naughton方案", "Balke方案", "YMCA方案"]:
            if test in instruction and test in self.knowledge_base:
                response = f"{self.knowledge_base[test]}\n\n"
                response += "根据测试结果，该受试者的心肺功能评估如下：\n"
                response += "1. 运动能力：能够完成测试的阶段和时间表明受试者的运动能力属于...水平。\n"
                response += "2. 心率反应：最大心率达到...次/分，符合/不符合年龄预测值，表明心血管系统的反应性...。\n"
                response += "3. 血压反应：运动过程中血压变化...，属于正常/异常反应。\n"
                response += "4. 运动建议：根据评估结果，建议进行...类型的运动，运动强度控制在...，每周运动...次，每次...分钟。\n"
                return response
        
        # 通用数据解读模板
        response = "根据测试结果，对受试者的评估如下：\n"
        response += "1. 测试结果分析：VO₂max（最大摄氧量）是评估心肺功能的金标准，该受试者的VO₂max为...ml/kg/min。\n"
        response += "2. 与标准值比较：根据ACSM标准，同年龄段健康人群的VO₂max参考值为...，该受试者的测试结果属于...水平。\n"
        response += "3. 功能水平评估：综合考虑心率、血压和主观疲劳感受，该受试者的心肺功能属于...水平。\n"
        response += "4. 运动建议：建议进行...类型的有氧运动，运动强度控制在最大心率的...%或RPE...，每周运动...次，每次...分钟。同时结合力量训练和柔韧性训练，以全面提高体适能水平。"
        
        return response
        
    def save_pairs(self):
        """保存指令-响应对到文件"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.instruction_response_pairs, f, ensure_ascii=False, indent=2)
        
        print(f"指令-响应对已保存到 {self.output_file}")
        
    def run(self):
        """运行整个生成流程"""
        # 1. 加载markdown文件
        self.load_markdown_files()
        
        # 2. 构建知识库
        self.build_knowledge_base()
        
        # 3. 生成指令-响应对
        self.generate_pairs()
        
        # 4. 保存结果
        self.save_pairs()

if __name__ == "__main__":
    # 创建生成器实例
    generator = ImprovedInstructionResponseGenerator(MARKDOWN_FOLDER, OUTPUT_FILE)
    
    # 运行生成流程
    generator.run()
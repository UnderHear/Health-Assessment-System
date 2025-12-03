import os

class Settings:
    def __init__(self):
        # 获取项目根目录
        # src/config/config.py -> src/config -> src -> project_root
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # RAG相关配置
        self.rag_components_path = os.path.join(self.project_root, "data/rag_components")
        # 使用本地嵌入模型
        self.embedding_model = os.path.join(self.project_root, "bge_small_embeddings")
        self.retriever_top_k = 10
        self.reranker_top_k = 5
        
        # 知识图谱配置 - 根据实际文件路径更新
        self.kg_triples_path = os.path.join(self.project_root, "data/cleaned_triples.json")
        self.kg_entities_path = os.path.join(self.project_root, "data/entity_with_vectors.json")
        self.kg_relations_path = os.path.join(self.project_root, "data/relation_with_vectors.json")
        
        # DeepSeek API配置
        self.deepseek_api_key = "sk-b316d0a918c54f5090ead8ea0112df7d"
        self.deepseek_api_base_url = "https://api.deepseek.com"
        self.deepseek_model = "deepseek-chat"
        self.deepseek_max_tokens = 4096
        
        # 日志配置
        self.log_level = "INFO"
        self.log_file = os.path.join(self.project_root, "app.log")
        
        # 评估配置
        self.score_weights = {
            "bmi": 0.1,
            "body_fat_rate": 0.1,
            "vital_capacity": 0.1,
            "max_oxygen_uptake": 0.1,
            "sit_and_reach": 0.1,
            "single_leg_stand": 0.1,
            "reaction_time": 0.1,
            "grip_strength": 0.1,
            "sit_ups_per_minute": 0.05,
            "push_ups": 0.05,
            "vertical_jump": 0.05,
            "high_knees_2min": 0.05,
            "sit_to_stand_30s": 0.05
    }

        # 数据目录配置
        self.data_dir = os.path.join(self.project_root, "data")
        
        # 运动处方配置
        self.prescription_stages = 3
        self.exercise_plan_template = os.path.join(self.project_root, "data/templates/exercise_plan.txt")
        
        # 确保数据目录存在
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """确保必要的目录存在"""
        directories = [
            self.rag_components_path,
            os.path.dirname(self.kg_triples_path),
            os.path.dirname(self.log_file)
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

# 创建全局配置实例
settings = Settings()
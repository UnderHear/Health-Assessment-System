import json
import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss

class KnowledgeGraphManager:
    """知识图谱管理类，负责知识图谱的加载、查询和相似实体查找"""
    def __init__(self, config):
        self.config = config
        self.triples = []  # 三元组列表
        self.entities = {}  # 实体映射表
        self.relations = {}  # 关系映射表
        self.entity_vectors = None  # 实体向量索引
        self.vector_model = None  # 向量模型
        self.entity_to_index = {}  # 实体到索引的映射
        self.index_to_entity = []  # 索引到实体的映射
        
        # 初始化知识图谱
        self._initialize_kg()
    
    def _initialize_kg(self):
        """初始化知识图谱"""
        try:
            # 加载实体和关系映射
            self._load_entities_and_relations()
            
            # 加载三元组数据
            self._load_triples()
            
            # 初始化向量模型并构建实体向量索引
            self._initialize_vector_model()
            self._build_entity_vector_index()
            
        except Exception as e:
            print(f"知识图谱初始化失败: {str(e)}")
    
    def _load_entities_and_relations(self):
        """加载实体和关系映射"""
        try:
            if hasattr(self.config, 'kg_entities_path') and self.config.kg_entities_path:
                with open(self.config.kg_entities_path, 'r', encoding='utf-8') as f:
                    self.entities = json.load(f)
            
            if hasattr(self.config, 'kg_relations_path') and self.config.kg_relations_path:
                with open(self.config.kg_relations_path, 'r', encoding='utf-8') as f:
                    self.relations = json.load(f)
        except Exception as e:
            print(f"加载实体和关系失败: {str(e)}")
    
    def _load_triples(self):
        """加载三元组数据"""
        import json
        try:
            if hasattr(self.config, 'kg_triples_path') and self.config.kg_triples_path:
                # 判断文件扩展名，使用不同的加载方法
                if self.config.kg_triples_path.endswith('.json'):
                    with open(self.config.kg_triples_path, 'r', encoding='utf-8') as f:
                        # 读取JSON数据
                        raw_triples = json.load(f)
                        # 转换字段名：head->subject, relation->predicate, tail->object
                        self.triples = []
                        for triple in raw_triples:
                            if 'head' in triple and 'relation' in triple and 'tail' in triple:
                                self.triples.append({
                                    'subject': triple['head'],
                                    'predicate': triple['relation'],
                                    'object': triple['tail']
                                })
                elif self.config.kg_triples_path.endswith('.csv'):
                    df = pd.read_csv(self.config.kg_triples_path, encoding='utf-8')
                    # 确保三元组格式正确
                    if 'subject' in df.columns and 'predicate' in df.columns and 'object' in df.columns:
                        self.triples = df.to_dict('records')
        except Exception as e:
            print(f"加载三元组失败: {str(e)}")
    
    def _initialize_vector_model(self):
        """初始化向量模型（优化：优先使用本地模型，失败时跳过）"""
        try:
            # 尝试从本地路径加载模型（如果存在）
            local_model_path = "bge-reranker-v2-m3"
            if os.path.exists(local_model_path) and os.path.isdir(local_model_path):
                print(f"正在尝试加载本地向量模型: {local_model_path}")
                self.vector_model = SentenceTransformer(local_model_path)
            elif hasattr(self.config, 'embedding_model') and self.config.embedding_model:
                print("尝试加载配置的嵌入模型...")
                self.vector_model = SentenceTransformer(self.config.embedding_model)
            # 如果所有加载尝试失败，也不会中断程序运行
        except Exception as e:
            print(f"初始化向量模型失败，但程序继续运行: {str(e)}")
    
    def _build_entity_vector_index(self):
        """构建实体向量索引"""
        if not self.vector_model or not self.entities:
            return
        
        try:
            # 收集所有实体名称
            entity_names = list(self.entities.keys())
            
            # 创建映射
            self.entity_to_index = {entity: i for i, entity in enumerate(entity_names)}
            self.index_to_entity = entity_names
            
            # 生成实体向量
            vectors = self.vector_model.encode(entity_names)
            vectors = np.array(vectors, dtype='float32')
            
            # 构建FAISS索引
            dimension = vectors.shape[1]
            self.entity_vectors = faiss.IndexFlatL2(dimension)
            self.entity_vectors.add(vectors)
            
        except Exception as e:
            print(f"构建实体向量索引失败: {str(e)}")
    
    def get_entity_vector(self, entity_name: str) -> Optional[np.ndarray]:
        """获取实体向量"""
        if not self.vector_model:
            return None
        
        try:
            return self.vector_model.encode([entity_name])[0]
        except Exception as e:
            print(f"获取实体向量失败: {str(e)}")
            return None
    
    def find_entity_by_similarity(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """通过相似度查找实体"""
        if not self.entity_vectors or not self.vector_model:
            return []
        
        try:
            # 生成查询向量
            query_vector = self.vector_model.encode([query])[0].reshape(1, -1)
            
            # 搜索相似实体
            distances, indices = self.entity_vectors.search(query_vector, top_k)
            
            # 格式化结果
            results = []
            for i, idx in enumerate(indices[0]):
                entity_name = self.index_to_entity[idx]
                similarity = 1 / (1 + distances[0][i])  # 将距离转换为相似度
                results.append((entity_name, float(similarity)))
            
            return results
        except Exception as e:
            print(f"查找相似实体失败: {str(e)}")
            return []
    
    def query_relations(self, entity: str, relation_type: Optional[str] = None) -> List[Dict[str, str]]:
        """查询实体的关系"""
        results = []
        
        for triple in self.triples:
            if triple['subject'] == entity and (relation_type is None or triple['predicate'] == relation_type):
                results.append({
                    'predicate': triple['predicate'],
                    'object': triple['object']
                })
        
        return results
    
    def get_entity_info(self, entity_name: str) -> Dict[str, any]:
        """获取实体的详细信息"""
        info = {
            'name': entity_name,
            'properties': {},
            'relations': []
        }
        
        # 添加实体属性
        if entity_name in self.entities:
            info['properties'] = self.entities[entity_name]
        
        # 添加实体关系
        info['relations'] = self.query_relations(entity_name)
        
        return info
    
    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, any]]:
        """搜索知识图谱"""
        # 1. 查找相似实体
        similar_entities = self.find_entity_by_similarity(query, top_k)
        
        # 2. 获取实体信息
        results = []
        for entity, score in similar_entities:
            entity_info = self.get_entity_info(entity)
            entity_info['relevance_score'] = score
            results.append(entity_info)
        
        return results
    
    def generate_knowledge_summary(self, query: str, max_length: int = 500) -> str:
        """生成知识摘要"""
        try:
            # 搜索相关知识
            search_results = self.search_knowledge(query)
            
            # 构建摘要
            summary_parts = []
            
            for result in search_results:
                # 添加实体名称
                part = f"【{result['name']}】"
                
                # 添加实体属性
                if result['properties']:
                    props = []
                    for key, value in result['properties'].items():
                        props.append(f"{key}: {value}")
                    part += "，".join(props)
                
                # 添加实体关系
                if result['relations']:
                    relations = []
                    for rel in result['relations']:
                        relations.append(f"{rel['predicate']}: {rel['object']}")
                    part += "，关系：" + "；".join(relations)
                
                summary_parts.append(part)
            
            # 组合摘要
            summary = "\n".join(summary_parts)
            
            # 控制长度
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary
        except Exception as e:
            print(f"生成知识摘要失败: {str(e)}")
            return ""
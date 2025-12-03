import os
import numpy as np
import faiss
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer, CrossEncoder

class FAISSRetriever:
    """基于FAISS的向量检索器"""
    def __init__(self, config):
        self.config = config
        self.index = None
        self.documents = []
        self.embedding_model = None
        self.dimension = 0
        
        # 初始化检索器
        self._initialize_retriever()
    
    def _initialize_retriever(self):
        """初始化检索器"""
        try:
            # 检查是否存在预计算的FAISS索引
            project_root = getattr(self.config, 'project_root', '.')
            faiss_index_path = os.path.join(project_root, "data/bge_faiss_index/bge_slice_index.faiss")
            embeddings_dir = os.path.join(project_root, "bge_small_embeddings")
            
            if os.path.exists(faiss_index_path) and os.path.exists(embeddings_dir):
                print(f"正在加载预计算的FAISS索引和嵌入模型")
                # 加载FAISS索引
                self.index = faiss.read_index(faiss_index_path)
                
                # 加载文档映射
                slice_mapping_path = os.path.join(embeddings_dir, "slice_mapping.json")
                if os.path.exists(slice_mapping_path):
                    with open(slice_mapping_path, 'r', encoding='utf-8') as f:
                        self.documents = json.load(f)
                
                # 设置维度（假设从索引中获取）
                self.dimension = self.index.d
                print(f"成功加载预计算索引，维度: {self.dimension}")
            else:
                # 加载嵌入模型
                if hasattr(self.config, 'embedding_model') and self.config.embedding_model:
                    self.embedding_model = SentenceTransformer(self.config.embedding_model)
                    # 获取模型维度
                    sample_embedding = self.embedding_model.encode(["sample"])
                    self.dimension = sample_embedding.shape[1]
                    
                    # 初始化FAISS索引
                    self.index = faiss.IndexFlatL2(self.dimension)
        except Exception as e:
            print(f"初始化检索器失败: {str(e)}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到检索器"""
        if not self.embedding_model or not self.index:
            return
        
        try:
            # 提取文档文本
            texts = [doc.get('content', '') for doc in documents]
            
            # 生成嵌入向量
            embeddings = self.embedding_model.encode(texts)
            embeddings = np.array(embeddings, dtype='float32')
            
            # 添加到FAISS索引
            self.index.add(embeddings)
            
            # 保存文档
            self.documents.extend(documents)
        except Exception as e:
            print(f"添加文档失败: {str(e)}")
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """检索与查询相关的文档"""
        if not self.embedding_model or not self.index or not self.documents:
            return []
        
        try:
            # 确定返回的文档数量
            k = top_k if top_k is not None else getattr(self.config, 'retriever_top_k', 10)
            
            # 生成查询向量
            query_embedding = self.embedding_model.encode([query])[0].reshape(1, -1)
            
            # 搜索相似文档
            distances, indices = self.index.search(query_embedding, k)
            
            # 格式化结果
            results = []
            for i, idx in enumerate(indices[0]):
                if 0 <= idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['distance'] = float(distances[0][i])
                    doc['relevance_score'] = 1 / (1 + float(distances[0][i]))  # 转换为相似度
                    results.append(doc)
            
            return results
        except Exception as e:
            print(f"检索文档失败: {str(e)}")
            return []
    
    def save_index(self, index_path: str):
        """保存FAISS索引"""
        try:
            if self.index:
                faiss.write_index(self.index, index_path)
        except Exception as e:
            print(f"保存索引失败: {str(e)}")
    
    def load_index(self, index_path: str):
        """加载FAISS索引"""
        try:
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
        except Exception as e:
            print(f"加载索引失败: {str(e)}")

class BGEReranker:
    """基于BGE的结果重排器"""
    def __init__(self, model_path: str = "bge-reranker-v2-m3"):
        self.reranker_model = None
        self.model_path = model_path
        
        # 初始化重排器
        self._initialize_reranker()
    
    def _initialize_reranker(self):
        """初始化重排器"""
        import os
        try:
            # 检查本地模型路径是否存在
            if os.path.exists(self.model_path) and os.path.isdir(self.model_path):
                print(f"正在加载本地重排器模型: {self.model_path}")
                self.reranker_model = CrossEncoder(self.model_path, trust_remote_code=True)
            else:
                print(f"本地模型路径不存在，尝试加载默认模型")
                self.reranker_model = CrossEncoder("BAAI/bge-reranker-large")
        except Exception as e:
            print(f"初始化重排器失败: {str(e)}")
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """对检索结果进行重排"""
        if not self.reranker_model or not documents:
            return documents
        
        try:
            # 准备重排输入
            pairs = [[query, doc.get('content', '')] for doc in documents]
            
            # 获取重排分数
            scores = self.reranker_model.predict(pairs)
            
            # 添加分数到文档
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
            
            # 按分数排序并返回前k个结果
            documents.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            
            return documents[:top_k]
        except Exception as e:
            print(f"重排文档失败: {str(e)}")
            return documents

class RAGPipeline:
    """RAG流水线，整合检索和重排功能"""
    def __init__(self, config):
        self.config = config
        self.retriever = FAISSRetriever(config)
        
        project_root = getattr(config, 'project_root', '.')
        reranker_model_path = os.path.join(project_root, "bge-reranker-v2-m3")
        self.reranker = BGEReranker(model_path=reranker_model_path)
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到RAG流水线"""
        self.retriever.add_documents(documents)
    
    def search(self, query: str, retrieve_top_k: Optional[int] = None, rerank_top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """执行RAG搜索"""
        # 1. 检索相关文档
        retrieved_docs = self.retriever.retrieve(query, retrieve_top_k)
        
        # 2. 重排检索结果
        top_k = rerank_top_k if rerank_top_k is not None else getattr(self.config, 'reranker_top_k', 5)
        reranked_docs = self.reranker.rerank(query, retrieved_docs, top_k)
        
        return reranked_docs
    
    def generate_context(self, query: str, max_length: int = 2000) -> str:
        """生成上下文文本"""
        # 执行搜索
        results = self.search(query)
        
        # 构建上下文
        context_parts = []
        total_length = 0
        
        for i, doc in enumerate(results):
            content = doc.get('content', '')
            # 检查长度限制
            if total_length + len(content) > max_length:
                # 截断文本以适应长度限制
                remaining_length = max_length - total_length
                content = content[:remaining_length]
                context_parts.append(content)
                break
            
            context_parts.append(content)
            total_length += len(content)
        
        return "\n\n".join(context_parts)
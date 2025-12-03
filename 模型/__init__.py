# 体质分析RAG系统（知识图谱增强版）包初始化文件

# 版本信息
__version__ = "1.0.0"

# 导出核心模块
from .config import settings
from .models import Gender, PhysicalTestInput, EvaluationResult, ExercisePhase, ExercisePrescription
from .kg_manager import KnowledgeGraphManager
from .rag_components import FAISSRetriever, BGEReranker, RAGPipeline
from .llm_client import DeepSeekAPIClient
from .data_loader import FitnessDataLoader
from .core_service import IntegratedFitnessRAGService

# 包说明
__all__ = [
    "settings",
    "Gender", "PhysicalTestInput", "EvaluationResult", "ExercisePhase", "ExercisePrescription",
    "KnowledgeGraphManager",
    "FAISSRetriever", "BGEReranker", "RAGPipeline",
    "DeepSeekAPIClient",
    "FitnessDataLoader",
    "IntegratedFitnessRAGService"
]

# 系统介绍
SYSTEM_DESCRIPTION = "体质分析RAG系统（知识图谱增强版）- 基于知识图谱和检索增强生成技术的个性化运动处方生成系统"
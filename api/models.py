"""
Pydantic模型定义

用于FastAPI的请求和响应数据验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ============ 闪卡相关模型 ============

class FlashcardTextRequest(BaseModel):
    """文本闪卡生成请求"""
    task_id: str = Field(..., description="任务ID（必填）")
    text: str = Field(..., description="要学习的文本内容")
    card_number: Optional[int] = Field(None, description="卡片数量（可选，不提供则由AI智能决定数量）")
    lang: str = Field("zh", description="语言（可选，默认中文）")


class FlashcardURLRequest(BaseModel):
    """URL闪卡生成请求"""
    task_id: str = Field(..., description="任务ID（必填）")
    url: str = Field(..., description="网页URL地址")
    card_number: Optional[int] = Field(None, description="卡片数量（可选，不提供则由AI智能决定数量）")
    lang: str = Field("zh", description="语言（可选，默认中文）")


class FlashcardTextSectionRequest(BaseModel):
    """文本章节闪卡生成请求"""
    text: str = Field(..., description="完整的学习材料文本内容")
    section_title: str = Field(..., description="章节标题")
    card_number: Optional[int] = Field(None, description="卡片数量（可选，不提供则由AI智能决定数量）")
    lang: str = Field("zh", description="语言（可选，默认中文）")


class FlashcardItem(BaseModel):
    """单个闪卡"""
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="答案")


class FlashcardResponse(BaseModel):
    """闪卡生成响应"""
    success: bool
    cards: Optional[List[FlashcardItem]] = None
    count: Optional[int] = None
    error: Optional[str] = None
    file_name: Optional[str] = None
    url: Optional[str] = None
    crawled_length: Optional[int] = None
    section_title: Optional[str] = None
    section_results: Optional[List[Dict[str, Any]]] = None


# ============ 大纲相关模型 ============

class CatalogTopicRequest(BaseModel):
    """话题大纲生成请求"""
    topic: str = Field(..., description="学习主题，如'Python编程基础'")
    lang: str = Field("zh", description="语言（可选，默认中文）")


class CatalogTextRequest(BaseModel):
    """文本大纲生成请求"""
    text: str = Field(..., description="完整的文本内容")
    lang: str = Field("zh", description="语言（可选，默认中文）")


class CatalogResponse(BaseModel):
    """大纲生成响应"""
    success: bool
    catalog: Optional[List[Dict[str, Any]]] = None
    file_name: Optional[str] = None
    error: Optional[str] = None

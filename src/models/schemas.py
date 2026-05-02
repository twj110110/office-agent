"""数据模型定义"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """文档类型"""
    WORK_SUMMARY = "work_summary"          # 工作总结
    OFFICIAL_DOC = "official_document"     # 公文
    REPORT = "report"                      # 汇报材料
    POLICY = "policy"                      # 政策文件
    NOTICE = "notice"                      # 通知
    ANNOUNCEMENT = "announcement"          # 公告
    PLAN = "plan"                          # 工作计划


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationResult(BaseModel):
    """校验结果"""
    passed: bool
    score: float = Field(..., ge=0.0, le=1.0)
    issues: List[str] = []
    suggestions: List[str] = []
    round_num: int = 1


class SubTask(BaseModel):
    """子任务"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = []
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class DocumentRequest(BaseModel):
    """文档生成请求"""
    doc_type: DocumentType
    title: str
    content_requirements: str
    keywords: List[str] = []
    tone: Literal["formal", "professional", "casual"] = "formal"
    max_length: int = Field(default=3000, le=10000)
    enable_validation: bool = True
    validation_rounds: int = Field(default=2, le=5)
    template_name: Optional[str] = None
    additional_context: Dict[str, Any] = {}


class DocumentResponse(BaseModel):
    """文档生成响应"""
    id: str
    title: str
    doc_type: DocumentType
    content: str
    formatted_content: str
    validation_results: List[ValidationResult] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class TaskRequest(BaseModel):
    """任务拆解请求"""
    task_description: str
    auto_execute: bool = True
    max_subtasks: int = Field(default=10, le=20)
    context: Dict[str, Any] = {}


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    description: str
    subtasks: List[SubTask]
    status: TaskStatus
    summary: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AgentMessage(BaseModel):
    """Agent消息"""
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentSession(BaseModel):
    """Agent会话"""
    id: str
    messages: List[AgentMessage]
    context: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

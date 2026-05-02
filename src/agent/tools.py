"""Agent工具集"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .base import Tool


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """列出所有工具"""
        return list(self._tools.values())
    
    def clear(self) -> None:
        """清空工具"""
        self._tools.clear()


# 全局工具注册表
tool_registry = ToolRegistry()


# ==================== 文档工具 ====================

async def generate_document_outline(
    doc_type: str,
    title: str,
    requirements: str,
    keywords: List[str] = None
) -> str:
    """生成文档大纲"""
    keywords = keywords or []
    
    outlines = {
        "work_summary": [
            "一、工作概述",
            "二、主要工作完成情况",
            "三、工作亮点与成效",
            "四、存在的问题与不足",
            "五、下一步工作计划"
        ],
        "official_document": [
            "一、背景与依据",
            "二、主要内容",
            "三、工作要求",
            "四、保障措施"
        ],
        "report": [
            "一、前言",
            "二、情况分析",
            "三、主要做法",
            "四、成效与经验",
            "五、建议与展望"
        ]
    }
    
    outline = outlines.get(doc_type, outlines["work_summary"])
    return json.dumps({
        "title": title,
        "type": doc_type,
        "outline": outline,
        "keywords": keywords,
        "estimated_length": 2000
    }, ensure_ascii=False)


async def search_policy_documents(
    query: str,
    category: str = "all",
    limit: int = 5
) -> str:
    """搜索政策文档（模拟）"""
    # 这里可以集成真实的政策数据库
    mock_results = [
        {
            "title": f"关于{query}的指导意见",
            "source": "国务院",
            "date": "2024-01-15",
            "summary": f"该文件对{query}相关工作提出了明确要求..."
        },
        {
            "title": f"{query}实施细则",
            "source": "相关部门",
            "date": "2024-02-20",
            "summary": f"细化了{query}的具体操作规范..."
        }
    ]
    return json.dumps(mock_results[:limit], ensure_ascii=False)


async def extract_key_points(text: str) -> str:
    """提取关键要点"""
    lines = text.split('\n')
    key_points = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith('•') or line.startswith('-') or 
                     line[0].isdigit() or '：' in line or ':' in line):
            key_points.append(line)
    
    return json.dumps({
        "total_points": len(key_points),
        "key_points": key_points[:20]
    }, ensure_ascii=False)


async def format_document(text: str, format_type: str = "official") -> str:
    """格式化文档"""
    # 基础格式化
    formatted = text.strip()
    
    # 添加标题层级
    lines = formatted.split('\n')
    result_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            result_lines.append('')
            continue
            
        # 检测标题
        if line.startswith('#') or (len(line) < 50 and 
                                     ('总结' in line or '报告' in line or 
                                      '计划' in line or '工作' in line)):
            if not line.startswith('#'):
                line = f"## {line}"
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


async def analyze_sentiment(text: str) -> str:
    """分析文本情感倾向"""
    positive_words = ['优秀', '成效', '突破', '创新', '领先', '提升', '增长']
    negative_words = ['问题', '不足', '困难', '挑战', '落后', '下降', '缺失']
    
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    
    sentiment = "neutral"
    if pos_count > neg_count + 2:
        sentiment = "positive"
    elif neg_count > pos_count + 2:
        sentiment = "negative"
    
    return json.dumps({
        "sentiment": sentiment,
        "positive_score": pos_count,
        "negative_score": neg_count,
        "confidence": min(1.0, (pos_count + neg_count) / 10)
    }, ensure_ascii=False)


async def calculate_statistics(data: List[float]) -> str:
    """计算统计数据"""
    if not data:
        return json.dumps({"error": "空数据"})
    
    total = sum(data)
    avg = total / len(data)
    max_val = max(data)
    min_val = min(data)
    
    return json.dumps({
        "count": len(data),
        "sum": round(total, 2),
        "average": round(avg, 2),
        "max": max_val,
        "min": min_val,
        "growth_rate": "待计算"
    }, ensure_ascii=False)


async def check_compliance(text: str, rules: List[str] = None) -> str:
    """合规性检查"""
    rules = rules or ['政治敏感', '数据准确', '格式规范']
    
    issues = []
    suggestions = []
    
    # 基础检查
    if len(text) < 100:
        issues.append("内容过短")
        suggestions.append("补充详细内容")
    
    if '数据' in text and not any(c.isdigit() for c in text):
        issues.append("提到数据但未提供具体数值")
        suggestions.append("添加具体数据支撑")
    
    return json.dumps({
        "passed": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
        "check_items": len(rules)
    }, ensure_ascii=False)


# 创建工具实例
document_outline_tool = Tool(
    name="generate_document_outline",
    description="根据文档类型生成大纲结构",
    parameters={
        "type": "object",
        "properties": {
            "doc_type": {
                "type": "string",
                "enum": ["work_summary", "official_document", "report", "policy", "notice"],
                "description": "文档类型"
            },
            "title": {
                "type": "string",
                "description": "文档标题"
            },
            "requirements": {
                "type": "string",
                "description": "内容要求"
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "关键词列表"
            }
        },
        "required": ["doc_type", "title", "requirements"]
    },
    func=generate_document_outline
)

policy_search_tool = Tool(
    name="search_policy_documents",
    description="搜索相关政策文档",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词"
            },
            "category": {
                "type": "string",
                "description": "文档类别"
            },
            "limit": {
                "type": "integer",
                "description": "返回数量限制"
            }
        },
        "required": ["query"]
    },
    func=search_policy_documents
)

extract_key_points_tool = Tool(
    name="extract_key_points",
    description="从文本中提取关键要点",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "输入文本"
            }
        },
        "required": ["text"]
    },
    func=extract_key_points
)

format_document_tool = Tool(
    name="format_document",
    description="格式化文档内容",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "文档内容"
            },
            "format_type": {
                "type": "string",
                "enum": ["official", "markdown", "plain"],
                "description": "格式类型"
            }
        },
        "required": ["text"]
    },
    func=format_document
)

analyze_sentiment_tool = Tool(
    name="analyze_sentiment",
    description="分析文本情感倾向",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "待分析文本"
            }
        },
        "required": ["text"]
    },
    func=analyze_sentiment
)

check_compliance_tool = Tool(
    name="check_compliance",
    description="检查内容合规性",
    parameters={
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "待检查文本"
            },
            "rules": {
                "type": "array",
                "items": {"type": "string"},
                "description": "检查规则"
            }
        },
        "required": ["text"]
    },
    func=check_compliance
)

# 注册所有工具
tool_registry.register(document_outline_tool)
tool_registry.register(policy_search_tool)
tool_registry.register(extract_key_points_tool)
tool_registry.register(format_document_tool)
tool_registry.register(analyze_sentiment_tool)
tool_registry.register(check_compliance_tool)

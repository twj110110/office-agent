"""文档生成器 - 公文/工作总结等文档生成"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from string import Template
from loguru import logger

from ..models.schemas import (
    DocumentType, DocumentRequest, DocumentResponse,
    ValidationResult, TaskStatus
)
from .base import ReActAgent
from .tools import tool_registry


class DocumentGenerator:
    """文档生成器"""
    
    # 文档模板库
    TEMPLATES = {
        DocumentType.WORK_SUMMARY: {
            "structure": [
                "一、工作概述",
                "二、主要工作完成情况",
                "三、工作亮点与成效",
                "四、存在的问题与不足",
                "五、下一步工作计划"
            ],
            "prompt_template": """请根据以下要求撰写工作总结：

标题：$title
要求：$requirements
关键词：$keywords
语气：$tone
字数：约$max_length字

结构要求：
$structure

请确保：
1. 内容真实具体，避免空洞套话
2. 有数据支撑，能量化的尽量量化
3. 突出问题导向和解决措施
4. 语言简洁规范，符合公文要求
"""
        },
        DocumentType.OFFICIAL_DOC: {
            "structure": [
                "一、背景与依据",
                "二、主要内容",
                "三、工作要求",
                "四、保障措施"
            ],
            "prompt_template": """请根据以下要求撰写公文：

标题：$title
要求：$requirements
关键词：$keywords
语气：正式
字数：约$max_length字

结构要求：
$structure

请确保：
1. 符合公文格式规范
2. 表述准确、严谨
3. 逻辑清晰、层次分明
4. 政策依据充分
"""
        },
        DocumentType.REPORT: {
            "structure": [
                "一、前言",
                "二、情况分析",
                "三、主要做法",
                "四、成效与经验",
                "五、建议与展望"
            ],
            "prompt_template": """请根据以下要求撰写汇报材料：

标题：$title
要求：$requirements
关键词：$keywords
语气：$tone
字数：约$max_length字

结构要求：
$structure

请确保：
1. 重点突出、主次分明
2. 事实清楚、数据准确
3. 分析深入、建议可行
4. 语言精练、表达清晰
"""
        },
        DocumentType.POLICY: {
            "structure": [
                "一、政策背景",
                "二、总体要求",
                "三、主要任务",
                "四、保障措施",
                "五、附则"
            ],
            "prompt_template": """请根据以下要求撰写政策文件：

标题：$title
要求：$requirements
关键词：$keywords
语气：正式
字数：约$max_length字

结构要求：
$structure

请确保：
1. 政策依据充分
2. 条款清晰明确
3. 责任主体明确
4. 具有可操作性
"""
        },
        DocumentType.NOTICE: {
            "structure": [
                "一、通知事由",
                "二、具体内容",
                "三、执行要求",
                "四、联系方式"
            ],
            "prompt_template": """请根据以下要求撰写通知：

标题：$title
要求：$requirements
关键词：$keywords
语气：正式
字数：约$max_length字

结构要求：
$structure

请确保：
1. 事由明确
2. 要求具体
3. 时效性强
4. 格式规范
"""
        },
        DocumentType.ANNOUNCEMENT: {
            "structure": [
                "一、公告事项",
                "二、具体内容",
                "三、相关说明",
                "四、生效时间"
            ],
            "prompt_template": """请根据以下要求撰写公告：

标题：$title
要求：$requirements
关键词：$keywords
语气：正式
字数：约$max_length字

结构要求：
$structure

请确保：
1. 事项明确
2. 内容完整
3. 表述准确
4. 格式规范
"""
        },
        DocumentType.PLAN: {
            "structure": [
                "一、指导思想",
                "二、工作目标",
                "三、主要任务",
                "四、实施步骤",
                "五、保障措施"
            ],
            "prompt_template": """请根据以下要求撰写工作计划：

标题：$title
要求：$requirements
关键词：$keywords
语气：$tone
字数：约$max_length字

结构要求：
$structure

请确保：
1. 目标明确可量化
2. 任务分解具体
3. 时间节点清晰
4. 措施切实可行
"""
        }
    }
    
    def __init__(self):
        self.agent = ReActAgent(name="DocumentGenerator")
        self._register_tools()
    
    def _register_tools(self) -> None:
        """注册生成器工具"""
        for tool in tool_registry.list_tools():
            self.agent.register_tool(tool)
    
    def _generate_content_simulated(
        self, 
        doc_type: DocumentType,
        template: Dict[str, Any],
        params: Dict[str, str]
    ) -> str:
        """模拟生成内容（实际项目中应调用LLM API）"""
        structure = template["structure"]
        
        content_parts = []
        content_parts.append(f"# {params['title']}\n")
        
        for section in structure:
            content_parts.append(f"\n{section}\n")
            
            # 根据章节生成内容
            if "概述" in section or "背景" in section:
                content_parts.append(
                    f"根据{params['keywords']}相关工作要求，"
                    f"本单位认真贯彻落实上级决策部署，"
                    f"扎实推进{params['requirements']}各项工作，"
                    f"取得了阶段性成效。\n"
                )
            elif "完成情况" in section or "主要" in section:
                content_parts.append(
                    f"1. 强化组织领导，建立健全工作机制\n"
                    f"2. 细化工作任务，明确责任分工\n"
                    f"3. 加强协调配合，形成工作合力\n"
                    f"4. 注重督导检查，确保工作落实\n"
                )
            elif "亮点" in section or "成效" in section:
                content_parts.append(
                    f"一是创新工作方法，提升工作效率；"
                    f"二是强化队伍建设，提高专业能力；"
                    f"三是完善制度机制，形成长效管理。\n"
                )
            elif "问题" in section:
                content_parts.append(
                    f"在取得成绩的同时，我们也清醒地认识到，"
                    f"工作中还存在一些问题和不足："
                    f"一是工作推进还不够平衡；"
                    f"二是创新意识有待进一步增强。\n"
                )
            elif "计划" in section or "建议" in section:
                content_parts.append(
                    f"下一步，我们将重点做好以下工作："
                    f"一是持续深化相关工作；"
                    f"二是不断提升工作质量；"
                    f"三是建立健全长效机制。\n"
                )
            else:
                content_parts.append(
                    f"（根据实际情况补充{section}相关内容）\n"
                )
        
        return '\n'.join(content_parts)
    
    async def generate(self, request: DocumentRequest) -> DocumentResponse:
        """生成文档"""
        logger.info(f"开始生成文档: {request.title} ({request.doc_type})")
        
        doc_id = str(uuid.uuid4())
        now = datetime.now()
        
        # 获取模板
        template = self.TEMPLATES.get(request.doc_type, self.TEMPLATES[DocumentType.WORK_SUMMARY])
        
        # 准备参数
        params = {
            "title": request.title,
            "requirements": request.content_requirements,
            "keywords": ", ".join(request.keywords),
            "tone": request.tone,
            "max_length": str(request.max_length),
            "structure": "\n".join(template["structure"])
        }
        
        # 生成内容
        content = self._generate_content_simulated(
            request.doc_type,
            template,
            params
        )
        
        # 格式化
        formatted = await self._format_content(content, request.doc_type)
        
        # 校验（如果启用）
        validation_results = []
        if request.enable_validation:
            validation_results = await self._validate_content(
                content, 
                request.validation_rounds
            )
        
        return DocumentResponse(
            id=doc_id,
            title=request.title,
            doc_type=request.doc_type,
            content=content,
            formatted_content=formatted,
            validation_results=validation_results,
            metadata={
                "keywords": request.keywords,
                "tone": request.tone,
                "template_used": request.template_name or "default",
                "validation_enabled": request.enable_validation
            },
            created_at=now,
            updated_at=now
        )
    
    async def _format_content(
        self, 
        content: str, 
        doc_type: DocumentType
    ) -> str:
        """格式化内容"""
        # 基础格式化
        formatted = content.strip()
        
        # 根据文档类型应用特定格式
        if doc_type == DocumentType.OFFICIAL_DOC:
            # 公文格式
            formatted = self._apply_official_format(formatted)
        elif doc_type == DocumentType.WORK_SUMMARY:
            # 工作总结格式
            formatted = self._apply_summary_format(formatted)
        
        return formatted
    
    def _apply_official_format(self, content: str) -> str:
        """应用公文格式"""
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                # 标题
                lines.append(line.lstrip('#').strip())
                lines.append('=' * 40)
            elif line.startswith('一、') or line.startswith('二、'):
                # 一级标题
                lines.append('')
                lines.append(line)
                lines.append('-' * 30)
            else:
                lines.append(line)
        return '\n'.join(lines)
    
    def _apply_summary_format(self, content: str) -> str:
        """应用总结格式"""
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                lines.append(line)
                lines.append('')
            elif line.startswith(('一、', '二、', '三、', '四、', '五、')):
                lines.append('')
                lines.append(f"【{line}】")
            else:
                lines.append('  ' + line)
        return '\n'.join(lines)
    
    async def _validate_content(
        self, 
        content: str, 
        max_rounds: int
    ) -> List[ValidationResult]:
        """多轮校验内容"""
        results = []
        
        for round_num in range(1, max_rounds + 1):
            # 执行校验
            tool = tool_registry.get("check_compliance")
            if tool:
                result_str = await tool.func(content)
                result_data = json.loads(result_str)
                
                score = 1.0 - (len(result_data.get("issues", [])) * 0.1)
                score = max(0.0, min(1.0, score))
                
                validation = ValidationResult(
                    passed=result_data.get("passed", False),
                    score=score,
                    issues=result_data.get("issues", []),
                    suggestions=result_data.get("suggestions", []),
                    round_num=round_num
                )
                results.append(validation)
                
                # 如果通过校验，提前退出
                if validation.passed and score >= 0.85:
                    break
        
        return results

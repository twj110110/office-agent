"""工具路由"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agent.tools import tool_registry


router = APIRouter()


class ToolCallRequest(BaseModel):
    """工具调用请求"""
    tool_name: str
    parameters: dict = {}


class FormatRequest(BaseModel):
    """格式化请求"""
    text: str
    format_type: str = "official"


class ValidationRequest(BaseModel):
    """校验请求"""
    text: str
    rules: list = None


@router.post("/tool-call")
async def call_tool(request: ToolCallRequest):
    """直接调用工具"""
    tool = tool_registry.get(request.tool_name)
    if not tool:
        raise HTTPException(
            status_code=404, 
            detail=f"工具 '{request.tool_name}' 未找到"
        )
    
    try:
        import asyncio
        if asyncio.iscoroutinefunction(tool.func):
            result = await tool.func(**request.parameters)
        else:
            result = tool.func(**request.parameters)
        
        return {
            "tool": request.tool_name,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"工具执行失败: {str(e)}"
        )


@router.post("/format")
async def format_text(request: FormatRequest):
    """格式化文本"""
    tool = tool_registry.get("format_document")
    if not tool:
        raise HTTPException(status_code=500, detail="格式化工具未找到")
    
    try:
        import asyncio
        if asyncio.iscoroutinefunction(tool.func):
            result = await tool.func(request.text, request.format_type)
        else:
            result = tool.func(request.text, request.format_type)
        
        return {"formatted_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"格式化失败: {str(e)}")


@router.post("/validate")
async def validate_text(request: ValidationRequest):
    """校验文本"""
    tool = tool_registry.get("check_compliance")
    if not tool:
        raise HTTPException(status_code=500, detail="校验工具未找到")
    
    try:
        import asyncio
        if asyncio.iscoroutinefunction(tool.func):
            result = await tool.func(request.text, request.rules or [])
        else:
            result = tool.func(request.text, request.rules or [])
        
        result_data = json.loads(result)
        return result_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"校验失败: {str(e)}")


@router.post("/extract-key-points")
async def extract_key_points(request: dict):
    """提取关键要点"""
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    tool = tool_registry.get("extract_key_points")
    if not tool:
        raise HTTPException(status_code=500, detail="工具未找到")
    
    try:
        import asyncio
        if asyncio.iscoroutinefunction(tool.func):
            result = await tool.func(text)
        else:
            result = tool.func(text)
        
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")


@router.post("/analyze-sentiment")
async def analyze_sentiment(request: dict):
    """情感分析"""
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    
    tool = tool_registry.get("analyze_sentiment")
    if not tool:
        raise HTTPException(status_code=500, detail="工具未找到")
    
    try:
        import asyncio
        if asyncio.iscoroutinefunction(tool.func):
            result = await tool.func(text)
        else:
            result = tool.func(text)
        
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

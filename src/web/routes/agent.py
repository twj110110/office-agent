"""Agent路由"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agent.base import ReActAgent
from ...agent.tools import tool_registry


router = APIRouter()


class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    session_id: str = None
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """对话响应"""
    response: str
    session_id: str
    tools_used: List[str] = []


# 会话管理
sessions: Dict[str, ReActAgent] = {}


def get_or_create_agent(session_id: str = None) -> tuple[ReActAgent, str]:
    """获取或创建Agent"""
    if session_id and session_id in sessions:
        return sessions[session_id], session_id
    
    # 创建新会话
    import uuid
    new_session_id = str(uuid.uuid4())
    agent = ReActAgent(name="OfficeAssistant")
    
    # 注册工具
    for tool in tool_registry.list_tools():
        agent.register_tool(tool)
    
    sessions[new_session_id] = agent
    return agent, new_session_id


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    try:
        agent, session_id = get_or_create_agent(request.session_id)
        
        # 执行对话
        response = await agent.run(
            request.message,
            request.context
        )
        
        # 获取使用的工具
        tools_used = []
        for thought in agent.thoughts:
            if thought.action and thought.action != "无":
                tools_used.append(thought.action)
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            tools_used=list(set(tools_used))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """获取会话历史"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话未找到")
    
    agent = sessions[session_id]
    return {
        "session_id": session_id,
        "memory": agent.memory,
        "thoughts": [
            {
                "step": t.step,
                "reasoning": t.reasoning,
                "action": t.action,
                "result": t.result
            }
            for t in agent.thoughts
        ]
    }


@router.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """清除会话"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "会话已清除"}
    
    raise HTTPException(status_code=404, detail="会话未找到")


@router.get("/tools")
async def get_tools():
    """获取可用工具列表"""
    tools = []
    for tool in tool_registry.list_tools():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        })
    
    return {"tools": tools}

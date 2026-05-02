"""Agent基类与核心实现"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, field

from loguru import logger


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]


@dataclass
class Thought:
    """思考过程"""
    step: int
    observation: str
    reasoning: str
    action: str
    action_input: Dict[str, Any]
    result: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str = "Agent", system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.tools: Dict[str, Tool] = {}
        self.memory: List[Dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        
    def register_tool(self, tool: Tool) -> None:
        """注册工具"""
        self.tools[tool.name] = tool
        logger.info(f"工具已注册: {tool.name}")
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取工具Schema列表"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """执行工具"""
        if tool_name not in self.tools:
            return f"错误: 工具 '{tool_name}' 未找到"
        
        tool = self.tools[tool_name]
        try:
            import asyncio
            if asyncio.iscoroutinefunction(tool.func):
                result = await tool.func(**params)
            else:
                result = tool.func(**params)
            return str(result) if result else "执行成功"
        except Exception as e:
            logger.error(f"工具执行错误 {tool_name}: {e}")
            return f"执行错误: {str(e)}"
    
    def add_to_memory(self, role: str, content: str, **kwargs) -> None:
        """添加到记忆"""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.memory.append(entry)
        # 限制记忆长度
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
    
    def get_memory_context(self, limit: int = 10) -> str:
        """获取记忆上下文"""
        recent = self.memory[-limit:] if self.memory else []
        return "\n".join([
            f"[{m['role']}] {m['content'][:200]}..."
            for m in recent
        ])
    
    @abstractmethod
    async def think(self, query: str, context: Dict[str, Any] = None) -> Thought:
        """思考过程"""
        pass
    
    @abstractmethod
    async def run(self, query: str, context: Dict[str, Any] = None) -> str:
        """运行Agent"""
        pass
    
    async def stream_run(self, query: str, context: Dict[str, Any] = None) -> AsyncGenerator[str, None]:
        """流式运行"""
        result = await self.run(query, context)
        yield result


class ReActAgent(BaseAgent):
    """ReAct模式Agent - 思考-行动-观察循环"""
    
    def __init__(self, name: str = "ReActAgent", max_iterations: int = 10):
        super().__init__(name)
        self.max_iterations = max_iterations
        self.thoughts: List[Thought] = []
        
    async def think(self, query: str, context: Dict[str, Any] = None) -> Thought:
        """单步思考"""
        # 构建思考提示
        tools_desc = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        memory = self.get_memory_context()
        
        prompt = f"""你是一个智能办公助手，使用ReAct模式（思考-行动-观察）解决问题。

可用工具:
{tools_desc}

历史记忆:
{memory}

当前问题: {query}

请按以下格式响应:
思考: [你的推理过程]
行动: [工具名称，如果没有则写"无"]
行动输入: [JSON格式的参数]

注意:
1. 如果不需要工具，直接给出最终答案
2. 行动输入必须是有效的JSON
3. 每次只执行一个工具
"""
        
        # 这里简化处理，实际应调用LLM
        thought = Thought(
            step=len(self.thoughts) + 1,
            observation=query,
            reasoning="分析用户需求...",
            action="无",
            action_input={}
        )
        
        return thought
    
    async def run(self, query: str, context: Dict[str, Any] = None) -> str:
        """运行ReAct循环"""
        logger.info(f"开始ReAct循环: {query[:100]}...")
        
        self.add_to_memory("user", query)
        self.thoughts = []
        
        final_answer = ""
        
        for i in range(self.max_iterations):
            # 思考
            thought = await self.think(query, context)
            self.thoughts.append(thought)
            
            logger.debug(f"步骤 {i+1}: {thought.reasoning[:100]}...")
            
            # 执行行动
            if thought.action and thought.action != "无":
                result = await self.execute_tool(
                    thought.action, 
                    thought.action_input
                )
                thought.result = result
                self.add_to_memory("tool", f"{thought.action}: {result}")
            else:
                # 最终答案
                final_answer = thought.reasoning
                break
        
        self.add_to_memory("assistant", final_answer)
        return final_answer

"""Agent测试"""

import pytest
import asyncio
from src.agent.base import ReActAgent
from src.agent.tools import tool_registry


@pytest.fixture
def agent():
    """创建测试Agent"""
    agent = ReActAgent(name="TestAgent")
    for tool in tool_registry.list_tools():
        agent.register_tool(tool)
    return agent


class TestReActAgent:
    """测试ReAct Agent"""
    
    def test_register_tool(self, agent):
        """测试工具注册"""
        assert len(agent.tools) > 0
        assert "format_document" in agent.tools
    
    def test_get_tool_schemas(self, agent):
        """测试获取工具Schema"""
        schemas = agent.get_tool_schemas()
        assert len(schemas) > 0
        assert all("function" in s for s in schemas)
    
    def test_add_to_memory(self, agent):
        """测试记忆添加"""
        agent.add_to_memory("user", "测试消息")
        assert len(agent.memory) == 1
        assert agent.memory[0]["role"] == "user"
    
    def test_get_memory_context(self, agent):
        """测试获取记忆上下文"""
        agent.add_to_memory("user", "消息1")
        agent.add_to_memory("assistant", "回复1")
        context = agent.get_memory_context()
        assert "user" in context
        assert "assistant" in context


class TestToolRegistry:
    """测试工具注册表"""
    
    def test_list_tools(self):
        """测试列出工具"""
        tools = tool_registry.list_tools()
        assert len(tools) > 0
        tool_names = [t.name for t in tools]
        assert "format_document" in tool_names
        assert "check_compliance" in tool_names

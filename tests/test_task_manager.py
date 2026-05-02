"""任务管理器测试"""

import pytest
from src.agent.task_manager import TaskManager, TaskNode
from src.models.schemas import TaskStatus


@pytest.fixture
def manager():
    """创建任务管理器"""
    return TaskManager(max_depth=3)


class TestTaskManager:
    """测试任务管理器"""
    
    def test_parse_task(self, manager):
        """测试任务解析"""
        task = manager.parse_task("撰写一份工作总结")
        
        assert task.id is not None
        assert len(task.children) > 0
        assert task.status == TaskStatus.PENDING
    
    def test_decompose_document_task(self, manager):
        """测试文档任务拆解"""
        subtasks = manager._decompose_document_task("撰写总结", {})
        assert len(subtasks) > 0
        assert any("需求" in s["name"] for s in subtasks)
    
    def test_decompose_analysis_task(self, manager):
        """测试分析任务拆解"""
        subtasks = manager._decompose_analysis_task("分析数据", {})
        assert len(subtasks) > 0
        assert any("数据" in s["name"] for s in subtasks)
    
    @pytest.mark.asyncio
    async def test_execute_leaf_task(self, manager):
        """测试执行叶子任务"""
        task = TaskNode(
            id="test",
            name="测试任务",
            description="测试"
        )
        
        await manager._execute_leaf_task(task)
        assert task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
    
    def test_aggregate_results(self, manager):
        """测试结果汇总"""
        root = TaskNode(id="root", name="根", description="根任务")
        child1 = TaskNode(id="c1", name="子1", description="子1", parent_id="root")
        child1.result = "结果1"
        child2 = TaskNode(id="c2", name="子2", description="子2", parent_id="root")
        child2.result = "结果2"
        
        root.children = [child1, child2]
        manager.tasks = {"root": root, "c1": child1, "c2": child2}
        
        result = manager._aggregate_results(root)
        assert "结果1" in result
        assert "结果2" in result
    
    def test_to_response(self, manager):
        """测试转换为响应"""
        root = manager.parse_task("测试任务")
        response = manager.to_response(root.id)
        
        assert response.id == root.id
        assert len(response.subtasks) > 0
        assert response.status == TaskStatus.PENDING

"""任务管理器 - 任务拆解与执行"""

import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from loguru import logger

from ..models.schemas import (
    TaskRequest, TaskResponse, SubTask, TaskStatus
)


@dataclass
class TaskNode:
    """任务节点"""
    id: str
    name: str
    description: str
    parent_id: Optional[str] = None
    children: List['TaskNode'] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    executor: Optional[Callable] = None
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskManager:
    """任务管理器"""
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.tasks: Dict[str, TaskNode] = {}
        self.executors: Dict[str, Callable] = {}
    
    def register_executor(self, task_type: str, executor: Callable) -> None:
        """注册任务执行器"""
        self.executors[task_type] = executor
        logger.info(f"执行器已注册: {task_type}")
    
    def parse_task(self, description: str, context: Dict[str, Any] = None) -> TaskNode:
        """解析任务为树形结构"""
        task_id = str(uuid.uuid4())
        
        # 智能任务拆解
        subtasks = self._decompose_task(description, context)
        
        root = TaskNode(
            id=task_id,
            name="主任务",
            description=description,
            children=[]
        )
        
        # 创建子任务节点
        for i, subtask_info in enumerate(subtasks):
            child = TaskNode(
                id=str(uuid.uuid4()),
                name=subtask_info.get("name", f"子任务{i+1}"),
                description=subtask_info.get("description", ""),
                parent_id=root.id,
                priority=subtask_info.get("priority", 1)
            )
            root.children.append(child)
            self.tasks[child.id] = child
            
            # 递归拆解深层任务
            if subtask_info.get("subtasks"):
                self._create_subtasks(child, subtask_info["subtasks"], depth=1)
        
        self.tasks[root.id] = root
        return root
    
    def _decompose_task(
        self, 
        description: str, 
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """智能任务拆解"""
        context = context or {}
        
        # 基于关键词的任务拆解
        if "撰写" in description or "生成" in description:
            return self._decompose_document_task(description, context)
        elif "分析" in description or "研究" in description:
            return self._decompose_analysis_task(description, context)
        elif "汇总" in description or "整理" in description:
            return self._decompose_aggregation_task(description, context)
        else:
            return self._decompose_generic_task(description, context)
    
    def _decompose_document_task(
        self, 
        description: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """拆解文档生成任务"""
        return [
            {
                "name": "需求分析",
                "description": "分析文档需求，确定类型、主题、目标受众",
                "priority": 1
            },
            {
                "name": "资料收集",
                "description": "收集相关背景资料、数据、政策文件",
                "priority": 2
            },
            {
                "name": "大纲设计",
                "description": "设计文档结构和内容大纲",
                "priority": 3
            },
            {
                "name": "内容撰写",
                "description": "撰写文档正文内容",
                "priority": 4
            },
            {
                "name": "校验优化",
                "description": "逻辑校验、格式排版、内容优化",
                "priority": 5
            }
        ]
    
    def _decompose_analysis_task(
        self, 
        description: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """拆解分析任务"""
        return [
            {
                "name": "问题定义",
                "description": "明确分析问题和目标",
                "priority": 1
            },
            {
                "name": "数据收集",
                "description": "收集相关数据和信息",
                "priority": 2
            },
            {
                "name": "数据分析",
                "description": "进行数据处理和深度分析",
                "priority": 3
            },
            {
                "name": "结论提炼",
                "description": "总结分析结论和建议",
                "priority": 4
            }
        ]
    
    def _decompose_aggregation_task(
        self, 
        description: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """拆解汇总任务"""
        return [
            {
                "name": "信息梳理",
                "description": "梳理需要汇总的信息来源",
                "priority": 1
            },
            {
                "name": "分类整理",
                "description": "按类别整理信息",
                "priority": 2
            },
            {
                "name": "内容整合",
                "description": "整合各部分内容",
                "priority": 3
            },
            {
                "name": "汇总输出",
                "description": "生成汇总报告",
                "priority": 4
            }
        ]
    
    def _decompose_generic_task(
        self, 
        description: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """通用任务拆解"""
        return [
            {
                "name": "任务理解",
                "description": "理解任务要求和目标",
                "priority": 1
            },
            {
                "name": "方案设计",
                "description": "设计执行方案",
                "priority": 2
            },
            {
                "name": "执行实施",
                "description": "执行具体任务",
                "priority": 3
            },
            {
                "name": "结果验证",
                "description": "验证任务结果",
                "priority": 4
            }
        ]
    
    def _create_subtasks(
        self, 
        parent: TaskNode, 
        subtasks: List[Dict[str, Any]],
        depth: int
    ) -> None:
        """递归创建子任务"""
        if depth >= self.max_depth:
            return
        
        for subtask_info in subtasks:
            child = TaskNode(
                id=str(uuid.uuid4()),
                name=subtask_info.get("name", "子任务"),
                description=subtask_info.get("description", ""),
                parent_id=parent.id,
                priority=subtask_info.get("priority", 1)
            )
            parent.children.append(child)
            self.tasks[child.id] = child
            
            if subtask_info.get("subtasks"):
                self._create_subtasks(child, subtask_info["subtasks"], depth + 1)
    
    async def execute_task(
        self, 
        task_id: str,
        parallel: bool = True
    ) -> TaskNode:
        """执行任务"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务未找到: {task_id}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        logger.info(f"开始执行任务: {task.name}")
        
        if task.children:
            # 执行子任务
            if parallel and len(task.children) > 1:
                await self._execute_parallel(task.children)
            else:
                await self._execute_sequential(task.children)
        else:
            # 执行叶子任务
            await self._execute_leaf_task(task)
        
        # 汇总结果
        task.result = self._aggregate_results(task)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        logger.info(f"任务完成: {task.name}")
        return task
    
    async def _execute_leaf_task(self, task: TaskNode) -> None:
        """执行叶子任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # 查找合适的执行器
            executor = None
            for keyword, exec_func in self.executors.items():
                if keyword in task.name or keyword in task.description:
                    executor = exec_func
                    break
            
            if executor:
                if asyncio.iscoroutinefunction(executor):
                    result = await executor(task.description)
                else:
                    result = executor(task.description)
                task.result = str(result)
            else:
                # 默认处理
                task.result = f"任务 '{task.name}' 执行完成（模拟）"
            
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"任务执行错误 {task.name}: {e}")
            task.status = TaskStatus.FAILED
            task.result = f"执行错误: {str(e)}"
        
        task.completed_at = datetime.now()
    
    async def _execute_sequential(self, tasks: List[TaskNode]) -> None:
        """串行执行"""
        for task in tasks:
            if task.children:
                await self._execute_sequential(task.children)
            else:
                await self._execute_leaf_task(task)
    
    async def _execute_parallel(self, tasks: List[TaskNode]) -> None:
        """并行执行"""
        coroutines = []
        
        for task in tasks:
            if task.children:
                coroutines.append(self._execute_parallel(task.children))
            else:
                coroutines.append(self._execute_leaf_task(task))
        
        await asyncio.gather(*coroutines, return_exceptions=True)
    
    def _aggregate_results(self, task: TaskNode) -> str:
        """汇总子任务结果"""
        if not task.children:
            return task.result or ""
        
        results = []
        for child in task.children:
            child_result = self._aggregate_results(child)
            results.append(f"【{child.name}】\n{child_result}")
        
        return "\n\n".join(results)
    
    def to_response(self, task_id: str) -> TaskResponse:
        """转换为响应对象"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务未找到: {task_id}")
        
        def convert_to_subtask(node: TaskNode) -> SubTask:
            return SubTask(
                id=node.id,
                name=node.name,
                description=node.description,
                status=node.status,
                dependencies=[node.parent_id] if node.parent_id else [],
                result=node.result,
                start_time=node.started_at,
                end_time=node.completed_at
            )
        
        def collect_subtasks(node: TaskNode) -> List[SubTask]:
            subtasks = [convert_to_subtask(node)]
            for child in node.children:
                subtasks.extend(collect_subtasks(child))
            return subtasks
        
        all_subtasks = collect_subtasks(task)
        
        return TaskResponse(
            id=task.id,
            description=task.description,
            subtasks=all_subtasks,
            status=task.status,
            summary=task.result,
            created_at=task.created_at,
            completed_at=task.completed_at
        )

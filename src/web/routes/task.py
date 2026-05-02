"""任务路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from ...models.schemas import TaskRequest, TaskResponse
from ..main import task_manager


router = APIRouter()


@router.post("/create", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """创建任务"""
    try:
        # 解析任务
        root_task = task_manager.parse_task(
            request.task_description,
            request.context
        )
        
        # 执行任务
        if request.auto_execute:
            await task_manager.execute_task(root_task.id)
        
        return task_manager.to_response(root_task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务创建失败: {str(e)}")


@router.post("/create-async")
async def create_task_async(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """异步创建并执行任务"""
    # 解析任务
    root_task = task_manager.parse_task(
        request.task_description,
        request.context
    )
    
    # 后台执行
    background_tasks.add_task(
        task_manager.execute_task,
        root_task.id
    )
    
    return {
        "task_id": root_task.id,
        "status": "processing",
        "message": "任务已提交，正在执行中"
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """获取任务状态"""
    try:
        return task_manager.to_response(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{task_id}/execute")
async def execute_task(task_id: str):
    """执行任务"""
    try:
        await task_manager.execute_task(task_id)
        return task_manager.to_response(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务执行失败: {str(e)}")


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str):
    """获取任务进度"""
    try:
        response = task_manager.to_response(task_id)
        
        total = len(response.subtasks)
        completed = sum(1 for t in response.subtasks 
                       if t.status.value == "completed")
        failed = sum(1 for t in response.subtasks 
                    if t.status.value == "failed")
        
        return {
            "task_id": task_id,
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": total - completed - failed,
            "progress": completed / total if total > 0 else 0,
            "status": response.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

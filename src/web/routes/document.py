"""文档路由"""

import os
import io
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse

from ...models.schemas import DocumentRequest, DocumentResponse, DocumentType
from ..main import doc_generator, settings


router = APIRouter()


@router.post("/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """生成文档"""
    try:
        response = await doc_generator.generate(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")


@router.post("/generate-async")
async def generate_document_async(
    request: DocumentRequest,
    background_tasks: BackgroundTasks
):
    """异步生成文档"""
    task_id = f"doc_{request.title}_{id(request)}"
    
    async def generate_and_save():
        response = await doc_generator.generate(request)
        # 保存到文件
        output_path = os.path.join(
            settings.DOC_OUTPUT_DIR,
            f"{response.id}.md"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.formatted_content)
    
    background_tasks.add_task(generate_and_save)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "文档生成任务已提交"
    }


@router.get("/templates")
async def get_templates(doc_type: DocumentType = Query(None)):
    """获取文档模板列表"""
    templates = {
        DocumentType.WORK_SUMMARY: [
            {"name": "年度工作总结", "description": "适用于年度工作总结报告"},
            {"name": "季度工作总结", "description": "适用于季度工作总结报告"},
            {"name": "项目总结", "description": "适用于项目完成后的总结"},
        ],
        DocumentType.OFFICIAL_DOC: [
            {"name": "请示", "description": "向上级请示事项"},
            {"name": "报告", "description": "向上级汇报工作"},
            {"name": "函", "description": "平行单位之间行文"},
        ],
        DocumentType.REPORT: [
            {"name": "工作汇报", "description": "常规工作汇报材料"},
            {"name": "调研报告", "description": "调研工作成果汇报"},
            {"name": "述职报告", "description": "个人或部门述职"},
        ],
    }
    
    if doc_type:
        return {"templates": templates.get(doc_type, [])}
    
    return {"templates": templates}


@router.post("/{doc_id}/export/{format}")
async def export_document(doc_id: str, format: str):
    """导出文档"""
    # 查找文档
    file_path = os.path.join(settings.DOC_OUTPUT_DIR, f"{doc_id}.md")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文档未找到")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if format.lower() == "txt":
        return StreamingResponse(
            io.StringIO(content),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={doc_id}.txt"}
        )
    elif format.lower() == "md":
        return StreamingResponse(
            io.StringIO(content),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={doc_id}.md"}
        )
    else:
        raise HTTPException(status_code=400, detail=f"不支持的格式: {format}")


@router.post("/batch-generate")
async def batch_generate(requests: List[DocumentRequest]):
    """批量生成文档"""
    results = []
    errors = []
    
    for i, request in enumerate(requests):
        try:
            response = await doc_generator.generate(request)
            results.append({
                "index": i,
                "success": True,
                "doc_id": response.id
            })
        except Exception as e:
            errors.append({
                "index": i,
                "success": False,
                "error": str(e)
            })
    
    return {
        "total": len(requests),
        "success": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }

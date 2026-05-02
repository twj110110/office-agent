"""FastAPI主应用"""

import os
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from loguru import logger

from ..core.config import settings
from ..models.schemas import (
    DocumentRequest, DocumentResponse,
    TaskRequest, TaskResponse,
    DocumentType, TaskStatus
)
from ..agent.document_generator import DocumentGenerator
from ..agent.task_manager import TaskManager
from .routes import document, task, agent, utils


# 配置日志
logger.add(
    "logs/office_agent.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)


# 全局服务实例
doc_generator: DocumentGenerator = None
task_manager: TaskManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global doc_generator, task_manager
    
    # 启动
    logger.info("正在初始化服务...")
    doc_generator = DocumentGenerator()
    task_manager = TaskManager()
    
    # 确保输出目录存在
    os.makedirs(settings.DOC_OUTPUT_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("服务初始化完成")
    yield
    
    # 关闭
    logger.info("正在关闭服务...")


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于智能Agent的全流程办公自动化助手",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(document.router, prefix=f"{settings.API_PREFIX}/documents", tags=["文档"])
app.include_router(task.router, prefix=f"{settings.API_PREFIX}/tasks", tags=["任务"])
app.include_router(agent.router, prefix=f"{settings.API_PREFIX}/agent", tags=["Agent"])
app.include_router(utils.router, prefix=f"{settings.API_PREFIX}/utils", tags=["工具"])


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Office Agent - 智能办公助手</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Office Agent</h1>
                <p>基于智能Agent的全流程办公自动化助手</p>
            </header>
            <nav>
                <a href="/app">进入应用</a>
                <a href="/docs">API文档</a>
                <a href="https://github.com/twj110110/office-agent">GitHub</a>
            </nav>
            <main>
                <section class="features">
                    <h2>核心功能</h2>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <h3>智能文档生成</h3>
                            <p>自动生成工作总结、公文、汇报材料等多种文档</p>
                        </div>
                        <div class="feature-card">
                            <h3>多轮逻辑校验</h3>
                            <p>自动检查内容逻辑、事实准确性、格式规范</p>
                        </div>
                        <div class="feature-card">
                            <h3>任务智能拆解</h3>
                            <p>复杂任务自动拆解，并行/串行执行</p>
                        </div>
                        <div class="feature-card">
                            <h3>格式自动排版</h3>
                            <p>一键生成符合规范的格式排版</p>
                        </div>
                    </div>
                </section>
            </main>
            <footer>
                <p>&copy; 2024 Office Agent. MIT License.</p>
            </footer>
        </div>
    </body>
    </html>
    """


@app.get("/app", response_class=HTMLResponse)
async def app_page():
    """应用页面"""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>应用界面加载中...</h1>")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "document_generator": doc_generator is not None,
            "task_manager": task_manager is not None
        }
    }


@app.get("/api/v1/document-types")
async def get_document_types():
    """获取支持的文档类型"""
    return {
        "types": [
            {"value": t.value, "label": _get_type_label(t)}
            for t in DocumentType
        ]
    }


def _get_type_label(doc_type: DocumentType) -> str:
    """获取文档类型标签"""
    labels = {
        DocumentType.WORK_SUMMARY: "工作总结",
        DocumentType.OFFICIAL_DOC: "公文",
        DocumentType.REPORT: "汇报材料",
        DocumentType.POLICY: "政策文件",
        DocumentType.NOTICE: "通知",
        DocumentType.ANNOUNCEMENT: "公告",
        DocumentType.PLAN: "工作计划"
    }
    return labels.get(doc_type, doc_type.value)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

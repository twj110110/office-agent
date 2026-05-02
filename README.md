# Office Agent - 智能办公自动化助手

基于智能 Agent 的全流程办公自动化助手，支持自主的公文 / 工作总结生成、多轮逻辑校验与格式排版。支持工具调用、任务拆解与结果自动汇总，能常态化应用于日常材料撰写、政策梳理。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 核心功能

### 1. 智能文档生成
- **多类型支持**：工作总结、公文、汇报材料、政策文件、通知、公告、工作计划
- **模板驱动**：内置多种常用文档模板，支持自定义扩展
- **智能填充**：基于内容要求自动生成符合规范的文档

### 2. 多轮逻辑校验
- **内容校验**：检查逻辑一致性、事实准确性
- **格式校验**：验证文档格式规范性
- **自动迭代**：支持多轮校验与自动优化

### 3. 格式自动排版
- **公文格式**：符合机关公文格式规范
- **一键排版**：自动调整标题层级、段落格式
- **多种格式**：支持 Markdown、纯文本等格式导出

### 4. 任务智能拆解
- **自动拆解**：复杂任务自动拆解为子任务
- **并行执行**：支持子任务并行处理
- **结果汇总**：自动汇总各子任务结果

### 5. 智能对话助手
- **ReAct 模式**：思考-行动-观察循环
- **工具调用**：支持多种工具的智能调用
- **上下文记忆**：支持多轮对话上下文

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/twj110110/office-agent.git
cd office-agent

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 运行

```bash
# 启动服务
python -m src.web.main

# 或
uvicorn src.web.main:app --reload
```

访问 http://localhost:8000 打开应用界面。

### API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
office-agent/
├── src/
│   ├── agent/              # Agent 核心实现
│   │   ├── base.py         # Agent 基类
│   │   ├── tools.py        # 工具集
│   │   ├── document_generator.py  # 文档生成器
│   │   └── task_manager.py # 任务管理器
│   ├── core/               # 核心配置
│   │   └── config.py       # 配置管理
│   ├── models/             # 数据模型
│   │   └── schemas.py      # Pydantic 模型
│   ├── web/                # Web 服务
│   │   ├── main.py         # FastAPI 主应用
│   │   └── routes/         # API 路由
│   └── utils/              # 工具函数
├── static/                 # 静态资源
│   ├── css/                # 样式文件
│   └── js/                 # JavaScript
├── templates/              # HTML 模板
├── tests/                  # 测试代码
├── docs/                   # 文档
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

## API 接口

### 文档生成

```http
POST /api/v1/documents/generate
```

请求示例：
```json
{
  "doc_type": "work_summary",
  "title": "2024年度工作总结",
  "content_requirements": "撰写一份年度工作总结，包含工作完成情况...",
  "keywords": ["数字化转型", "工作总结", "2024"],
  "tone": "formal",
  "max_length": 3000,
  "enable_validation": true,
  "validation_rounds": 2
}
```

### 智能对话

```http
POST /api/v1/agent/chat
```

请求示例：
```json
{
  "message": "帮我写一份关于数字化转型的年度工作总结",
  "context": {}
}
```

### 任务管理

```http
POST /api/v1/tasks/create
```

请求示例：
```json
{
  "task_description": "撰写一份年度工作总结，需要分析各部门数据...",
  "auto_execute": true,
  "context": {}
}
```

## 工具集

| 工具名 | 描述 |
|--------|------|
| generate_document_outline | 生成文档大纲 |
| search_policy_documents | 搜索政策文档 |
| extract_key_points | 提取关键要点 |
| format_document | 格式化文档 |
| analyze_sentiment | 情感分析 |
| check_compliance | 合规性检查 |

## 配置

创建 `.env` 文件：

```env
# 应用配置
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# LLM 配置 (可选，用于增强生成能力)
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 文档配置
DOC_OUTPUT_DIR=output
VALIDATION_MAX_ROUNDS=3
```

## 使用场景

### 场景1：快速生成工作总结

```python
from src.agent.document_generator import DocumentGenerator
from src.models.schemas import DocumentRequest, DocumentType

async def example():
    generator = DocumentGenerator()
    request = DocumentRequest(
        doc_type=DocumentType.WORK_SUMMARY,
        title="2024年度工作总结",
        content_requirements="总结全年数字化转型工作...",
        keywords=["数字化", "转型", "创新"],
        enable_validation=True
    )
    result = await generator.generate(request)
    print(result.content)
```

### 场景2：智能任务拆解

```python
from src.agent.task_manager import TaskManager

async def example():
    manager = TaskManager()
    task = manager.parse_task("撰写一份全面的年度工作报告")
    await manager.execute_task(task.id)
    response = manager.to_response(task.id)
    print(response.summary)
```

### 场景3：多轮对话助手

```python
from src.agent.base import ReActAgent
from src.agent.tools import tool_registry

async def example():
    agent = ReActAgent()
    for tool in tool_registry.list_tools():
        agent.register_tool(tool)
    
    response = await agent.run("帮我分析这份工作总结的优缺点")
    print(response)
```

## 开发计划

- [x] 核心Agent框架
- [x] 文档生成器
- [x] 多轮校验系统
- [x] 任务管理器
- [x] Web API
- [x] 前端界面
- [ ] LLM 集成增强
- [ ] 更多文档模板
- [ ] 文档导出（Word/PDF）
- [ ] 协作编辑功能
- [ ] 知识库集成

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

[MIT](LICENSE) License

## 作者

**twj110110** - [GitHub](https://github.com/twj110110)

---

> Office Agent - 让办公更智能，让创作更高效！

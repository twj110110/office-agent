"""文档生成器测试"""

import pytest
from src.agent.document_generator import DocumentGenerator
from src.models.schemas import DocumentRequest, DocumentType


@pytest.fixture
def generator():
    """创建文档生成器"""
    return DocumentGenerator()


@pytest.fixture
def sample_request():
    """创建示例请求"""
    return DocumentRequest(
        doc_type=DocumentType.WORK_SUMMARY,
        title="测试工作总结",
        content_requirements="测试内容要求",
        keywords=["测试", "工作"],
        tone="formal",
        max_length=1000,
        enable_validation=False
    )


class TestDocumentGenerator:
    """测试文档生成器"""
    
    @pytest.mark.asyncio
    async def test_generate(self, generator, sample_request):
        """测试文档生成"""
        response = await generator.generate(sample_request)
        
        assert response.id is not None
        assert response.title == sample_request.title
        assert response.doc_type == sample_request.doc_type
        assert len(response.content) > 0
        assert len(response.formatted_content) > 0
    
    def test_templates_exist(self, generator):
        """测试模板存在"""
        for doc_type in DocumentType:
            assert doc_type in generator.TEMPLATES
    
    def test_template_structure(self, generator):
        """测试模板结构"""
        template = generator.TEMPLATES[DocumentType.WORK_SUMMARY]
        assert "structure" in template
        assert "prompt_template" in template
        assert len(template["structure"]) > 0
    
    @pytest.mark.asyncio
    async def test_validation(self, generator):
        """测试校验功能"""
        request = DocumentRequest(
            doc_type=DocumentType.WORK_SUMMARY,
            title="测试",
            content_requirements="测试",
            enable_validation=True,
            validation_rounds=2
        )
        
        response = await generator.generate(request)
        assert len(response.validation_results) > 0
    
    def test_official_format(self, generator):
        """测试公文格式"""
        content = "# 标题\n正文内容"
        formatted = generator._apply_official_format(content)
        assert len(formatted) > 0
    
    def test_summary_format(self, generator):
        """测试总结格式"""
        content = "# 标题\n一、第一部分"
        formatted = generator._apply_summary_format(content)
        assert "【一、" in formatted

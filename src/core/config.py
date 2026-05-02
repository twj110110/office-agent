"""配置管理"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "Office Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # LLM配置
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    
    # 文档配置
    DOC_TEMPLATE_DIR: str = "templates"
    DOC_OUTPUT_DIR: str = "output"
    DOC_MAX_LENGTH: int = 10000
    
    # 校验配置
    VALIDATION_MAX_ROUNDS: int = 3
    VALIDATION_THRESHOLD: float = 0.85
    
    # 任务配置
    TASK_MAX_DEPTH: int = 5
    TASK_TIMEOUT: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

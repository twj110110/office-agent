"""辅助工具函数"""

import re
import uuid
from datetime import datetime
from typing import List, Dict, Any


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())[:8]


def clean_text(text: str) -> str:
    """清理文本"""
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    return text


def split_sentences(text: str) -> List[str]:
    """分句"""
    # 中文分句
    sentences = re.split(r'([。！？；\n])', text)
    result = []
    current = ""
    
    for part in sentences:
        current += part
        if part in '。！？；\n':
            if current.strip():
                result.append(current.strip())
            current = ""
    
    if current.strip():
        result.append(current.strip())
    
    return result


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """简单关键词提取"""
    # 停用词
    stopwords = set([
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人',
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
        '你', '会', '着', '没有', '看', '好', '自己', '这', '那'
    ])
    
    # 提取词（简单实现）
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
    word_freq = {}
    
    for word in words:
        if word not in stopwords and len(word) >= 2:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # 返回高频词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def format_datetime(dt: datetime = None) -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y年%m月%d日')


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def count_words(text: str) -> int:
    """统计字数"""
    # 中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    # 英文单词
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def detect_doc_type(text: str) -> str:
    """检测文档类型"""
    indicators = {
        'work_summary': ['总结', '年度', '季度', '工作'],
        'official_document': ['请示', '报告', '函', '通知'],
        'report': ['汇报', '调研', '分析', '报告'],
        'policy': ['政策', '意见', '办法', '规定'],
        'notice': ['通知', '公告', '通告'],
        'plan': ['计划', '方案', '规划']
    }
    
    scores = {}
    text_lower = text.lower()
    
    for doc_type, keywords in indicators.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[doc_type] = score
    
    # 返回得分最高的类型
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    
    return 'general'


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    # 去除非法字符
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    # 限制长度
    filename = truncate_text(filename, 100)
    return filename

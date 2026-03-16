"""
飞书笔记转GitHub笔记工具

将飞书导出的文档转换为GitHub兼容的Markdown格式，
支持生成完整的GitHub仓库结构。

主要功能:
- 解析飞书JSON格式文档
- 支持多种Markdown扩展（数学公式、Mermaid图表、代码高亮）
- 生成仓库目录结构
- 支持批量转换
"""

__version__ = "1.0.0"
__author__ = "Feishu2GitHub Team"

from .feishu_parser import FeishuParser, Document, Block
from .markdown_generator import MarkdownGenerator, EnhancedMarkdownGenerator
from .repo_generator import RepoGenerator, RepoConfig, Chapter
from .style_formatter import EnhancedStyleFormatter, StyleFormatter, TableFormatter

__all__ = [
    'FeishuParser',
    'FeishuMarkdownParser',
    'Document',
    'Block',
    'MarkdownGenerator',
    'EnhancedMarkdownGenerator',
    'RepoGenerator',
    'RepoConfig',
    'Chapter',
    'EnhancedStyleFormatter',
    'StyleFormatter',
    'TableFormatter',
    'Converter',
]
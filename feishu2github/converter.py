#!/usr/bin/env python3
import argparse
import os
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from .feishu_parser import FeishuParser, FeishuMarkdownParser, Document
    from .markdown_generator import MarkdownGenerator, EnhancedMarkdownGenerator
    from .repo_generator import RepoGenerator, RepoConfig, Chapter, ChapterOrganizer, AutoChapterGenerator
    from .style_formatter import EnhancedStyleFormatter, BadgeGenerator
except ImportError:
    from feishu_parser import FeishuParser, FeishuMarkdownParser, Document
    from markdown_generator import MarkdownGenerator, EnhancedMarkdownGenerator
    from repo_generator import RepoGenerator, RepoConfig, Chapter, ChapterOrganizer, AutoChapterGenerator
    from style_formatter import EnhancedStyleFormatter, BadgeGenerator


class Converter:
    def __init__(self, 
                 use_gfm: bool = True,
                 enable_math: bool = True,
                 enable_mermaid: bool = True,
                 enable_toc: bool = True,
                 enable_style: bool = True):
        self.use_gfm = use_gfm
        self.enable_math = enable_math
        self.enable_mermaid = enable_mermaid
        self.enable_toc = enable_toc
        self.enable_style = enable_style
        
        self.parser = FeishuParser()
        self.markdown_parser = FeishuMarkdownParser()
        self.md_generator = EnhancedMarkdownGenerator(
            use_gfm=use_gfm,
            enable_math=enable_math,
            enable_mermaid=enable_mermaid
        ) if use_gfm else MarkdownGenerator(use_gfm=use_gfm)
        
        self.style_formatter = EnhancedStyleFormatter() if enable_style else None

    def convert_file(self, input_path: str, output_path: str) -> bool:
        try:
            input_path = Path(input_path)
            
            if not input_path.exists():
                print(f"错误: 输入文件不存在: {input_path}")
                return False
            
            ext = input_path.suffix.lower()
            
            if ext == '.json':
                doc = self.parser.parse_file(str(input_path))
            elif ext == '.md':
                content = input_path.read_text(encoding='utf-8')
                doc = self.markdown_parser.parse_from_markdown_export(content)
            else:
                print(f"错误: 不支持的文件格式: {ext}")
                return False
            
            markdown_content = self.md_generator.generate(doc)
            
            if self.enable_style and self.style_formatter and not self.enable_toc:
                markdown_content = self.style_formatter.add_table_of_contents(markdown_content)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            output_path.write_text(markdown_content, encoding='utf-8')
            
            print(f"转换成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def convert_to_repo(self, input_path: str, output_dir: str, 
                       repo_name: str = "", description: str = "",
                       author: str = "") -> bool:
        try:
            input_path = Path(input_path)
            
            if not input_path.exists():
                print(f"错误: 输入文件不存在: {input_path}")
                return False
            
            ext = input_path.suffix.lower()
            
            if ext == '.json':
                doc = self.parser.parse_file(str(input_path))
            elif ext == '.md':
                content = input_path.read_text(encoding='utf-8')
                doc = self.markdown_parser.parse_from_markdown_export(content)
            else:
                print(f"错误: 不支持的文件格式: {ext}")
                return False
            
            markdown_content = self.md_generator.generate(doc)
            
            doc_structure = self.parser.get_document_structure(doc)
            
            if not repo_name:
                repo_name = doc.title if doc.title else "feishu-notes"
            
            chapters = AutoChapterGenerator.from_document_structure(doc_structure)
            
            if not chapters:
                chapters = [
                    Chapter(title="概述", level=1, file_name="overview.md", content=""),
                    Chapter(title="内容", level=1, file_name="content.md", content=markdown_content)
                ]
            else:
                for i, chapter in enumerate(chapters):
                    if i == 0:
                        chapter.content = markdown_content
                    else:
                        chapter.content = ""
            
            config = RepoConfig(
                repo_name=repo_name,
                description=description or doc.metadata.get('description', ''),
                author=author,
                chapters=chapters,
                output_dir=output_dir
            )
            
            generator = RepoGenerator(config)
            generator.generate()
            
            print(f"仓库生成成功: {output_dir}")
            return True
            
        except Exception as e:
            print(f"仓库生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def batch_convert(self, input_dir: str, output_dir: str) -> int:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            print(f"错误: 输入目录不存在: {input_dir}")
            return 0
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.md']:
                relative_path = file_path.relative_to(input_path)
                output_file = output_path / relative_path.with_suffix('.md')
                
                if self.convert_file(str(file_path), str(output_file)):
                    success_count += 1
        
        return success_count


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════╗
║          飞书笔记转GitHub笔记工具 - Feishu2GitHub            ║
║                   Version 1.0.0                            ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='飞书笔记转GitHub笔记工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换单个文件
  python -m feishu2github.converter -i input.json -o output.md
  
  # 转换并生成仓库结构
  python -m feishu2github.converter -i input.json -o ./output --repo-name "我的笔记"
  
  # 批量转换目录
  python -m feishu2github.converter -i ./feishu_docs -o ./markdown_docs --batch
  
  # 禁用高级特性
  python -m feishu2github.converter -i input.json -o output.md --no-math --no-mermaid --no-toc
        """
    )
    
    parser.add_argument('-i', '--input', required=True, help='输入文件或目录路径')
    parser.add_argument('-o', '--output', required=True, help='输出文件或目录路径')
    parser.add_argument('--repo-name', default='', help='仓库名称（生成仓库结构时使用）')
    parser.add_argument('--description', default='', help='仓库描述')
    parser.add_argument('--author', default='', help='作者名称')
    parser.add_argument('--batch', action='store_true', help='批量转换模式')
    parser.add_argument('--no-gfm', action='store_true', help='禁用GitHub Flavored Markdown扩展')
    parser.add_argument('--no-math', action='store_true', help='禁用数学公式支持')
    parser.add_argument('--no-mermaid', action='store_true', help='禁用Mermaid图表支持')
    parser.add_argument('--no-toc', action='store_true', help='禁用目录自动生成')
    parser.add_argument('--no-style', action='store_true', help='禁用样式美化')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细输出')
    
    args = parser.parse_args()
    
    converter = Converter(
        use_gfm=not args.no_gfm,
        enable_math=not args.no_math,
        enable_mermaid=not args.no_mermaid,
        enable_toc=not args.no_toc,
        enable_style=not args.no_style
    )
    
    input_path = Path(args.input)
    
    generate_repo = args.repo_name or args.description or args.author
    
    if args.batch or input_path.is_dir():
        if not input_path.is_dir():
            print(f"错误: 批量模式需要输入目录: {args.input}")
            sys.exit(1)
        
        success_count = converter.batch_convert(args.input, args.output)
        print(f"\n批量转换完成: 成功转换 {success_count} 个文件")
        
    elif generate_repo or args.output.endswith('/') or (Path(args.output).exists() and Path(args.output).is_dir()):
        success = converter.convert_to_repo(
            args.input, 
            args.output,
            repo_name=args.repo_name,
            description=args.description,
            author=args.author
        )
        sys.exit(0 if success else 1)
    
    else:
        success = converter.convert_file(args.input, args.output)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

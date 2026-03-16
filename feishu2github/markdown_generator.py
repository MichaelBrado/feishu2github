import re
from typing import List, Dict, Any, Optional
from .feishu_parser import Block, Document


class MarkdownGenerator:
    def __init__(self, use_gfm: bool = True):
        self.use_gfm = use_gfm
    
    def generate(self, doc: Document) -> str:
        lines = []
        
        if doc.title:
            lines.append(f"# {doc.title}")
            lines.append("")
        
        for block in doc.blocks:
            block_lines = self._generate_block(block)
            lines.extend(block_lines)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_block(self, block: Block) -> List[str]:
        generators = {
            'heading': self._generate_heading,
            'paragraph': self._generate_paragraph,
            'bullet': self._generate_bullet,
            'ordered': self._generate_ordered,
            'code': self._generate_code,
            'table': self._generate_table,
            'image': self._generate_image,
            'quote': self._generate_quote,
            'divider': self._generate_divider,
            'callout': self._generate_callout,
            'mermaid': self._generate_mermaid,
            'math': self._generate_math,
        }
        
        generator = generators.get(block.block_type, self._generate_text)
        return generator(block)
    
    def _generate_heading(self, block: Block) -> List[str]:
        prefix = '#' * block.level
        return [f"{prefix} {block.content}"]
    
    def _generate_paragraph(self, block: Block) -> List[str]:
        return [self._process_inline_formatting(block.content)]
    
    def _generate_text(self, block: Block) -> List[str]:
        return [str(block.content)]
    
    def _generate_bullet(self, block: Block) -> List[str]:
        lines = []
        items = block.content if isinstance(block.content, list) else [block.content]
        for item in items:
            if item:
                content = self._process_inline_formatting(str(item))
                lines.append(f"- {content}")
        return lines

    def _generate_ordered(self, block: Block) -> List[str]:
        lines = []
        items = block.content if isinstance(block.content, list) else [block.content]
        number = block.attributes.get('number', 1)
        for item in items:
            if item:
                content = self._process_inline_formatting(str(item))
                lines.append(f"{number}. {content}")
                number += 1
        return lines

    def _generate_code(self, block: Block) -> List[str]:
        lines = []
        language = block.language or ''
        
        if self.use_gfm and language:
            lines.append(f"```{language}")
        else:
            lines.append("```")
        
        if block.content:
            lines.append(block.content.rstrip())
        
        lines.append("```")
        
        return lines
    
    def _generate_table(self, block: Block) -> List[str]:
        if not block.content or len(block.content) == 0:
            return []
        
        rows = block.content
        lines = []
        
        for i, row in enumerate(rows):
            row_str = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
            lines.append(row_str)
            
            if i == 0:
                header_row = '| ' + ' | '.join(['---'] * len(row)) + ' |'
                lines.append(header_row)
        
        return lines
    
    def _generate_image(self, block: Block) -> List[str]:
        alt_text = block.attributes.get('alt', 'image')
        return [f"![{alt_text}]({block.content})"]
    
    def _generate_quote(self, block: Block) -> List[str]:
        content = self._process_inline_formatting(block.content)
        return [f"> {content}"]
    
    def _generate_divider(self, block: Block) -> List[str]:
        return ["---"]
    
    def _generate_callout(self, block: Block) -> List[str]:
        callout_type = block.attributes.get('callout_type', 'info')
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'danger': '❌',
            'success': '✅',
            'tip': '💡'
        }
        emoji = emoji_map.get(callout_type, 'ℹ️')
        content = self._process_inline_formatting(block.content)
        return [f"> **{emoji} {callout_type.upper()}**: {content}"]
    
    def _generate_mermaid(self, block: Block) -> List[str]:
        lines = ["```mermaid"]
        if block.content:
            lines.append(block.content)
        lines.append("```")
        return lines
    
    def _generate_math(self, block: Block) -> List[str]:
        if block.attributes.get('inline'):
            return [f"${block.content}$"]
        else:
            return [f"$$\n{block.content}\n$$"]
    
    def _process_inline_formatting(self, text: str) -> str:
        if not text:
            return ''
        
        text = str(text)
        
        text = re.sub(r'\*\*(.+?)\*\*', r'**\1**', text)
        text = re.sub(r'\*(.+?)\*', r'*\1*', text)
        text = re.sub(r'__(.+?)__', r'__\1__', text)
        text = re.sub(r'_(.+?)_', r'_\1_', text)
        text = re.sub(r'~~(.+?)~~', r'~~\1~~', text)
        text = re.sub(r'`(.+?)`', r'`\1`', text)
        
        return text


class EnhancedMarkdownGenerator(MarkdownGenerator):
    def __init__(self, use_gfm: bool = True, enable_math: bool = True, 
                 enable_mermaid: bool = True):
        super().__init__(use_gfm)
        self.enable_math = enable_math
        self.enable_mermaid = enable_mermaid
    
    def generate(self, doc: Document) -> str:
        lines = []
        
        if doc.title:
            lines.append(f"# {doc.title}")
            lines.append("")
        
        headings_for_toc = []
        for block in doc.blocks:
            if block.block_type == 'heading':
                headings_for_toc.append(block)
        
        if headings_for_toc:
            lines.append("## 目录")
            lines.append("")
            lines.append(self._generate_toc(headings_for_toc))
            lines.append("")
        
        for block in doc.blocks:
            block_lines = self._generate_block(block)
            lines.extend(block_lines)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_toc(self, headings: List[Block]) -> str:
        lines = []
        for heading in headings:
            indent = "  " * (heading.level - 1)
            anchor = self._generate_anchor(heading.content)
            lines.append(f"{indent}- [{heading.content}](#{anchor})")
        
        return '\n'.join(lines)
    
    def _generate_anchor(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        return text
    
    def _generate_code(self, block: Block) -> List[str]:
        lines = []
        language = block.language or ''
        
        if self.use_gfm and language:
            lines.append(f"```{language}")
        else:
            lines.append("```")
        
        if block.content:
            lines.append(block.content.rstrip())
        
        lines.append("```")
        
        return lines
    
    def _generate_math(self, block: Block) -> List[str]:
        if self.enable_math:
            if block.attributes.get('inline'):
                return [f"${block.content}$"]
            else:
                return [f"$$\n{block.content}\n$$"]
        else:
            return [f"```\n{block.content}\n```"]
    
    def _generate_mermaid(self, block: Block) -> List[str]:
        if self.enable_mermaid:
            lines = ["```mermaid"]
            if block.content:
                lines.append(block.content)
            lines.append("```")
            return lines
        else:
            return self._generate_code(block)

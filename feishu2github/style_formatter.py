import re
from typing import List, Dict, Optional
from .feishu_parser import Block, Document


class StyleFormatter:
    def __init__(self):
        self.emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'danger': '❌',
            'success': '✅',
            'tip': '💡',
            'note': '📝',
        }
    
    def format_callout(self, content: str, callout_type: str = 'info') -> str:
        emoji = self.emoji_map.get(callout_type, 'ℹ️')
        return f"> **{emoji} {callout_type.upper()}**: {content}"
    
    def format_badge(self, text: str, color: str = 'blue') -> str:
        color_map = {
            'blue': '007AD9',
            'green': '28A745',
            'red': 'DC3545',
            'yellow': 'FFC107',
            'orange': 'FD7E14',
            'purple': '6F42C1',
        }
        color_code = color_map.get(color.lower(), '007AD9')
        return f"[![{text}](https://img.shields.io/badge/{text}-{color_code}?style=flat-square)](https://example.com)"
    
    def format_anchor(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        return text


class TableFormatter:
    def __init__(self):
        pass
    
    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        lines = []
        
        header_line = '| ' + ' | '.join(headers) + ' |'
        lines.append(header_line)
        
        separator = '| ' + ' | '.join(['---'] * len(headers)) + ' |'
        lines.append(separator)
        
        for row in rows:
            row_line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
            lines.append(row_line)
        
        return '\n'.join(lines)
    
    def format_striped_table(self, headers: List[str], rows: List[List[str]]) -> str:
        lines = []
        
        header_line = '| ' + ' | '.join(headers) + ' |'
        lines.append(header_line)
        
        separator = '| ' + ' | '.join([':--'] * len(headers)) + ' |'
        lines.append(separator)
        
        for i, row in enumerate(rows):
            row_line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
            lines.append(row_line)
        
        return '\n'.join(lines)


class EnhancedStyleFormatter:
    def __init__(self):
        self.style_formatter = StyleFormatter()
        self.table_formatter = TableFormatter()
    
    def add_table_of_contents(self, content: str, min_heading_level: int = 2) -> str:
        lines = content.split('\n')
        
        toc_lines = []
        in_toc = False
        content_lines = []
        
        for line in lines:
            if line.strip() == '## 目录':
                in_toc = True
                toc_lines.append(line)
                continue
            
            if in_toc:
                if line.startswith('## ') and not line.startswith('###'):
                    in_toc = False
                    content_lines.append(line)
                else:
                    toc_lines.append(line)
            else:
                content_lines.append(line)
        
        if not toc_lines:
            return content
        
        return '\n'.join(content_lines)
    
    def add_anchor_links(self, content: str) -> str:
        lines = content.split('\n')
        result = []
        
        for line in lines:
            if line.startswith('### ') or line.startswith('## '):
                level = line.count('#')
                text = line.lstrip('#').strip()
                anchor = self.style_formatter.format_anchor(text)
                line = f"{line} {{ #{anchor} }}"
            
            result.append(line)
        
        return '\n'.join(result)
    
    def format_blockquote(self, content: str, style: str = 'info') -> str:
        emoji = self.style_formatter.emoji_map.get(style, 'ℹ️')
        return f"> **{emoji} {style.upper()}**: {content}"


class BadgeGenerator:
    @staticmethod
    def generate_shield_badge(label: str, value: str, color: str = 'blue') -> str:
        color_map = {
            'blue': '007AD9',
            'green': '28A745',
            'red': 'DC3545',
            'yellow': 'FFC107',
            'orange': 'FD7E14',
            'purple': '6F42C1',
            'grey': '6C757D',
        }
        color_code = color_map.get(color.lower(), '007AD9')
        label_encoded = label.replace(' ', '%20')
        value_encoded = value.replace(' ', '%20')
        return f"![{label}](https://img.shields.io/badge/{label_encoded}-{value_encoded}?style=flat-square&color={color_code})"
    
    @staticmethod
    def generate_version_badge(version: str) -> str:
        return BadgeGenerator.generate_shield_badge('Version', version, 'blue')
    
    @staticmethod
    def generate_license_badge(license_name: str) -> str:
        return BadgeGenerator.generate_shield_badge('License', license_name, 'green')
    
    @staticmethod
    def generate_python_version_badge(version: str = '3.8+') -> str:
        return BadgeGenerator.generate_shield_badge('Python', version, 'blue')
    
    @staticmethod
    def generate_stars_badge(stars: str) -> str:
        return BadgeGenerator.generate_shield_badge('Stars', stars, 'yellow')
    
    @staticmethod
    def generate_forks_badge(forks: str) -> str:
        return BadgeGenerator.generate_shield_badge('Forks', forks, 'green')

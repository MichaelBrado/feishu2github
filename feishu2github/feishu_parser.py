import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class Block:
    block_type: str
    content: Any
    level: int = 0
    language: Optional[str] = None
    children: List['Block'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    title: str = ""
    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeishuParser:
    def __init__(self):
        self.block_type_mapping = {
            'text': self._parse_text,
            'heading1': self._parse_heading,
            'heading2': self._parse_heading,
            'heading3': self._parse_heading,
            'heading4': self._parse_heading,
            'heading5': self._parse_heading,
            'heading6': self._parse_heading,
            'paragraph': self._parse_paragraph,
            'bullet': self._parse_bullet,
            'bullet_list': self._parse_bullet,
            'unordered': self._parse_bullet,
            'ordered': self._parse_ordered,
            'numbered_list': self._parse_ordered,
            'number': self._parse_ordered,
            'code': self._parse_code,
            'code_block': self._parse_code,
            'pre': self._parse_code,
            'table': self._parse_table,
            'image': self._parse_image,
            'quote': self._parse_quote,
            'blockquote': self._parse_quote,
            'divider': self._parse_divider,
            'hr': self._parse_divider,
            'callout': self._parse_callout,
            'callout_block': self._parse_callout,
            'mermaid': self._parse_mermaid,
            'math': self._parse_math,
            'math_block': self._parse_math,
            'equation': self._parse_math,
        }

    def parse_file(self, file_path: str) -> Document:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self.parse(data)

    def parse(self, data: Dict[str, Any]) -> Document:
        doc = Document()
        
        if 'title' in data:
            doc.title = self._extract_text_from_rich_text(data['title'])
        
        if 'metadata' in data:
            doc.metadata = data['metadata']
        
        blocks_data = data.get('blocks', data.get('body', {}).get('blocks', []))
        
        for block_data in blocks_data:
            block = self._parse_block(block_data)
            if block:
                doc.blocks.append(block)
        
        return doc

    def _parse_block(self, block_data: Dict[str, Any]) -> Optional[Block]:
        block_type = block_data.get('type', 'text')
        
        if block_type in self.block_type_mapping:
            return self.block_type_mapping[block_type](block_data)
        elif block_type == 'container':
            return self._parse_container(block_data)
        else:
            return self._parse_text(block_data)

    def _parse_container(self, block_data: Dict[str, Any]) -> Optional[Block]:
        children = block_data.get('children', [])
        if not children:
            return None
        
        container_type = block_data.get('container_type', 'div')
        if container_type.startswith('heading'):
            level = int(container_type.replace('heading', ''))
            child_block = self._parse_block(children[0]) if children else None
            if child_block:
                child_block.level = level
                return child_block
        
        blocks = []
        for child in children:
            block = self._parse_block(child)
            if block:
                blocks.append(block)
        
        if blocks:
            return Block(
                block_type='container',
                content=blocks,
                children=blocks
            )
        return None

    def _extract_text_from_rich_text(self, rich_text: Any) -> str:
        if isinstance(rich_text, str):
            return rich_text
        
        if isinstance(rich_text, list):
            text_parts = []
            for item in rich_text:
                if isinstance(item, dict):
                    text = item.get('text', '')
                    if text:
                        text_parts.append(text)
                elif isinstance(item, str):
                    text_parts.append(item)
            return ''.join(text_parts)
        
        if isinstance(rich_text, dict):
            return rich_text.get('text', str(rich_text))
        
        return str(rich_text)

    def _extract_links_from_rich_text(self, rich_text: Any) -> List[Dict[str, str]]:
        links = []
        
        if isinstance(rich_text, list):
            for item in rich_text:
                if isinstance(item, dict):
                    link = item.get('link')
                    if link:
                        links.append({
                            'text': item.get('text', ''),
                            'url': link.get('url', '')
                        })
        
        return links

    def _parse_text(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('text', ''))
        links = self._extract_links_from_rich_text(block_data.get('text', []))
        
        return Block(
            block_type='text',
            content=content,
            attributes={'links': links}
        )

    def _parse_heading(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('text', ''))
        level = block_data.get('level', 1)
        
        if block_data.get('type') == 'heading1':
            level = 1
        elif block_data.get('type') == 'heading2':
            level = 2
        elif block_data.get('type') == 'heading3':
            level = 3
        elif block_data.get('type') == 'heading4':
            level = 4
        elif block_data.get('type') == 'heading5':
            level = 5
        elif block_data.get('type') == 'heading6':
            level = 6
        
        return Block(
            block_type='heading',
            content=content,
            level=level
        )

    def _parse_paragraph(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('text', ''))
        links = self._extract_links_from_rich_text(block_data.get('text', []))
        
        return Block(
            block_type='paragraph',
            content=content,
            attributes={'links': links}
        )

    def _parse_bullet(self, block_data: Dict[str, Any]) -> Block:
        items = block_data.get('items', [])
        if not items and 'text' in block_data:
            content = self._extract_text_from_rich_text(block_data.get('text', ''))
            items = [content] if content else []
        else:
            parsed_items = []
            for item in items:
                if isinstance(item, dict):
                    text = self._extract_text_from_rich_text(item.get('text', ''))
                elif isinstance(item, str):
                    text = item
                else:
                    text = str(item)
                if text:
                    parsed_items.append(text)
            items = parsed_items
        
        return Block(
            block_type='bullet',
            content=items,
            attributes={'items': items}
        )

    def _parse_ordered(self, block_data: Dict[str, Any]) -> Block:
        items = block_data.get('items', [])
        if not items and 'text' in block_data:
            content = self._extract_text_from_rich_text(block_data.get('text', ''))
            items = [content] if content else []
            number = block_data.get('number', 1)
        else:
            parsed_items = []
            for item in items:
                if isinstance(item, dict):
                    text = self._extract_text_from_rich_text(item.get('text', ''))
                elif isinstance(item, str):
                    text = item
                else:
                    text = str(item)
                if text:
                    parsed_items.append(text)
            items = parsed_items
            number = 1
        
        return Block(
            block_type='ordered',
            content=items,
            attributes={'number': number, 'items': items}
        )

    def _parse_code(self, block_data: Dict[str, Any]) -> Block:
        code = block_data.get('code', '')
        if not code and 'text' in block_data:
            code = self._extract_text_from_rich_text(block_data.get('text', ''))
        language = block_data.get('language', '').lower()
        
        return Block(
            block_type='code',
            content=code,
            language=language
        )

    def _parse_table(self, block_data: Dict[str, Any]) -> Block:
        rows = []
        
        for row in block_data.get('cells', []):
            row_data = []
            for cell in row:
                if isinstance(cell, dict):
                    cell_text = self._extract_text_from_rich_text(cell.get('text', ''))
                else:
                    cell_text = self._extract_text_from_rich_text(cell)
                row_data.append(cell_text)
            rows.append(row_data)
        
        return Block(
            block_type='table',
            content=rows
        )

    def _parse_image(self, block_data: Dict[str, Any]) -> Block:
        image_url = block_data.get('url', block_data.get('image', {}).get('url', ''))
        token = block_data.get('token', '')
        
        return Block(
            block_type='image',
            content=image_url,
            attributes={'token': token}
        )

    def _parse_quote(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('text', ''))
        
        return Block(
            block_type='quote',
            content=content
        )

    def _parse_divider(self, block_data: Dict[str, Any]) -> Block:
        return Block(
            block_type='divider',
            content=''
        )

    def _parse_callout(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('text', ''))
        callout_type = block_data.get('callout_type', 'info')
        
        return Block(
            block_type='callout',
            content=content,
            attributes={'callout_type': callout_type}
        )

    def _parse_mermaid(self, block_data: Dict[str, Any]) -> Block:
        content = self._extract_text_from_rich_text(block_data.get('code', ''))
        
        return Block(
            block_type='mermaid',
            content=content
        )

    def _parse_math(self, block_data: Dict[str, Any]) -> Block:
        content = block_data.get('text', '')
        if not content:
            content = block_data.get('formula', '')
        if isinstance(content, list):
            content = self._extract_text_from_rich_text(content)
        
        return Block(
            block_type='math',
            content=content
        )

    def get_document_structure(self, doc: Document) -> Dict[str, Any]:
        structure = {
            'title': doc.title,
            'block_count': len(doc.blocks),
            'headings': [],
            'code_blocks': [],
            'tables': [],
            'images': [],
            'links': []
        }
        
        for block in doc.blocks:
            if block.block_type == 'heading':
                structure['headings'].append({
                    'level': block.level,
                    'text': block.content
                })
            elif block.block_type == 'code':
                structure['code_blocks'].append({
                    'language': block.language,
                    'lines': len(block.content.split('\n'))
                })
            elif block.block_type == 'table':
                structure['tables'].append({
                    'rows': len(block.content),
                    'cols': len(block.content[0]) if block.content else 0
                })
            elif block.block_type == 'image':
                structure['images'].append(block.content)
            
            links = block.attributes.get('links', [])
            structure['links'].extend(links)
        
        return structure


class FeishuMarkdownParser:
    def parse_from_markdown_export(self, content: str) -> Document:
        doc = Document()
        lines = content.split('\n')
        
        in_code_block = False
        code_language = ''
        code_content = []
        
        for line in lines:
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_language = line[3:].strip()
                    code_content = []
                else:
                    code_block = Block(
                        block_type='code',
                        content='\n'.join(code_content),
                        language=code_language
                    )
                    doc.blocks.append(code_block)
                    in_code_block = False
                    code_language = ''
                    code_content = []
                continue
            
            if in_code_block:
                code_content.append(line)
                continue
            
            if line.startswith('# '):
                doc.title = line[2:]
                doc.blocks.append(Block(block_type='heading', content=line[2:], level=1))
            elif line.startswith('## '):
                doc.blocks.append(Block(block_type='heading', content=line[3:], level=2))
            elif line.startswith('### '):
                doc.blocks.append(Block(block_type='heading', content=line[4:], level=3))
            elif line.startswith('- '):
                doc.blocks.append(Block(block_type='bullet', content=[line[2:]]))
            elif line.strip():
                doc.blocks.append(Block(block_type='paragraph', content=line))
        
        return doc

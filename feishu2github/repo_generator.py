from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Chapter:
    title: str
    level: int = 1
    file_name: str = ""
    content: str = ""
    children: List['Chapter'] = field(default_factory=list)


@dataclass
class RepoConfig:
    repo_name: str
    description: str = ""
    author: str = ""
    chapters: List[Chapter] = field(default_factory=list)
    output_dir: str = "."
    image_dir: str = "images"


class RepoGenerator:
    def __init__(self, config: RepoConfig):
        self.config = config
        self.root_dir = Path(config.output_dir)
    
    def generate(self) -> None:
        self._create_directory_structure()
        self._generate_readme()
        self._generate_chapters()
        self._generate_gitignore()
        self._generate_config()

    def _create_directory_structure(self) -> None:
        dirs_to_create = [
            self.root_dir,
            self.root_dir / self.config.image_dir,
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_readme(self) -> None:
        readme_content = self._build_readme()
        readme_path = self.root_dir / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')

    def _build_readme(self) -> str:
        lines = []
        
        lines.append(f"# {self.config.repo_name}")
        lines.append("")
        
        if self.config.description:
            lines.append(f"_{self.config.description}_")
            lines.append("")
        
        lines.append("## 目录")
        lines.append("")
        
        for chapter in self.config.chapters:
            indent = "  " * (chapter.level - 1)
            anchor = chapter.file_name.replace('.md', '')
            
            if chapter.children:
                lines.append(f"{indent}- [{chapter.title}](#{anchor})")
                for child in chapter.children:
                    child_indent = "  " * (child.level - 1)
                    child_anchor = child.file_name.replace('.md', '')
                    lines.append(f"{child_indent}- [{child.title}](#{child_anchor})")
            else:
                lines.append(f"{indent}- [{chapter.title}](#{anchor})")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 快速开始")
        lines.append("")
        lines.append("```bash")
        lines.append(f"# 克隆仓库")
        lines.append(f"git clone https://github.com/your-username/{self.config.repo_name}.git")
        lines.append("```")
        lines.append("")
        
        if self.config.author:
            lines.append(f"**作者**: {self.config.author}")
            lines.append("")
        
        return '\n'.join(lines)

    def _generate_chapters(self) -> None:
        for chapter in self.config.chapters:
            if chapter.content:
                chapter_path = self.root_dir / chapter.file_name
                chapter_path.write_text(chapter.content, encoding='utf-8')
            
            for child in chapter.children:
                if child.content:
                    child_path = self.root_dir / child.file_name
                    child_path.write_text(child.content, encoding='utf-8')

    def _generate_gitignore(self) -> None:
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        gitignore_path = self.root_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding='utf-8')

    def _generate_config(self) -> None:
        config_content = """{
  "converter": "feishu2github",
  "version": "1.0.0",
  "repo_name": """ + self.config.repo_name + """
}
"""
        config_path = self.root_dir / ".feishu2github.json"
        config_path.write_text(config_content, encoding='utf-8')


class ChapterOrganizer:
    @staticmethod
    def organize_by_level(chapters: List[Chapter]) -> Dict[int, List[Chapter]]:
        organized = {}
        for chapter in chapters:
            if chapter.level not in organized:
                organized[chapter.level] = []
            organized[chapter.level].append(chapter)
        return organized
    
    @staticmethod
    def organize_by_topic(chapters: List[Chapter], topics: List[str]) -> Dict[str, List[Chapter]]:
        organized = {topic: [] for topic in topics}
        organized['Other'] = []
        
        for chapter in chapters:
            assigned = False
            for topic in topics:
                if topic.lower() in chapter.title.lower():
                    organized[topic].append(chapter)
                    assigned = True
                    break
            if not assigned:
                organized['Other'].append(chapter)
        
        return organized


class AutoChapterGenerator:
    @staticmethod
    def from_document_structure(doc_structure: Dict[str, Any]) -> List[Chapter]:
        chapters = []
        
        title = doc_structure.get('title', '')
        headings = doc_structure.get('headings', [])
        
        if not headings:
            if title:
                return [Chapter(title=title, level=1, file_name="README.md", content="")]
            return []
        
        current_chapter = None
        for heading in headings:
            level = heading.get('level', 1)
            text = heading.get('text', '')
            
            if level == 1:
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = Chapter(
                    title=text,
                    level=level,
                    file_name=AutoChapterGenerator._generate_filename(text)
                )
            elif level == 2:
                if current_chapter:
                    child = Chapter(
                        title=text,
                        level=level,
                        file_name=AutoChapterGenerator._generate_filename(text)
                    )
                    current_chapter.children.append(child)
        
        if current_chapter:
            chapters.append(current_chapter)
        
        if not chapters and title:
            chapters.append(Chapter(title=title, level=1, file_name="README.md", content=""))
        
        return chapters
    
    @staticmethod
    def _generate_filename(title: str) -> str:
        import re
        filename = title.lower()
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'\s+', '-', filename)
        return f"{filename}.md"

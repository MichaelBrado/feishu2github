# feishu2github

飞书笔记转GitHub笔记工具 - 将飞书文档转换为GitHub友好的Markdown格式

## 功能特点

- 解析飞书JSON格式文档
- 支持多种Markdown扩展（数学公式、Mermaid图表、代码高亮）
- 生成仓库目录结构
- 支持批量转换

## 安装

```bash
pip install -e .
```

## 使用方法

```bash
# 转换单个文件
python -m feishu2github.converter -i input.json -o output.md

# 转换并生成仓库结构
python -m feishu2github.converter -i input.json -o ./output --repo-name "我的笔记"

# 批量转换目录
python -m feishu2github.converter -i ./feishu_docs -o ./markdown_docs --batch
```

## License

MIT

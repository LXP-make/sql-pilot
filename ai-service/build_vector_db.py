import json
import os
import chromadb
import re

class MarkdownChunker:
    """Markdown文档分块器"""
    
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text):
        """简单高效的文本分块"""
        chunks = []
        text = text.strip()
        
        while len(text) > self.chunk_size:
            # 在合适的位置分割
            split_pos = self.chunk_size
            
            # 优先在换行或标点处分割
            for i in range(self.chunk_size, max(0, self.chunk_size - 100), -1):
                if text[i] in '\n。！？；\r':
                    split_pos = i + 1
                    break
            
            chunk = text[:split_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            # 保留重叠部分
            text = text[split_pos - self.chunk_overlap:]
        
        if text.strip():
            chunks.append(text.strip())
        
        return chunks
    
    def parse_markdown(self, content):
        """解析Markdown文件"""
        lines = content.split('\n')
        sections = []
        current_section = {"title": "", "content": "", "code_blocks": [], "tables": []}
        in_code = False
        code_lang = ""
        code_content = []
        
        for line in lines:
            # 代码块处理
            if line.startswith('```'):
                if in_code:
                    current_section["code_blocks"].append({
                        "language": code_lang,
                        "content": '\n'.join(code_content)
                    })
                    in_code = False
                    code_content = []
                else:
                    in_code = True
                    code_lang = line[3:].strip()
                continue
            
            if in_code:
                code_content.append(line)
                continue
            
            # 标题处理
            if line.startswith('#'):
                if current_section["content"] or current_section["title"]:
                    sections.append(current_section)
                level = len(line) - len(line.lstrip('#'))
                current_section = {
                    "title": line.lstrip('#').strip(),
                    "content": "",
                    "code_blocks": [],
                    "tables": []
                }
                continue
            
            # 表格处理
            if line.startswith('|') and current_section:
                if not current_section["content"].strip():
                    # 可能是表格的开始
                    current_section["content"] += line + '\n'
                else:
                    # 添加到内容
                    current_section["content"] += line + '\n'
                continue
            
            # 普通内容
            current_section["content"] += line + '\n'
        
        if current_section["content"] or current_section["title"]:
            sections.append(current_section)
        
        return sections
    
    def chunk_markdown(self, filepath):
        """处理Markdown文件"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        sections = self.parse_markdown(content)
        all_chunks = []
        doc_title = os.path.basename(filepath).replace('.md', '')
        
        for section in sections:
            section_context = f"文档: {doc_title}\n"
            if section["title"]:
                section_context += f"标题: {section['title']}\n"
            
            # 处理文本内容
            if section["content"]:
                content_chunks = self.chunk_text(section["content"])
                for i, chunk in enumerate(content_chunks):
                    chunk_text = section_context + f"正文: {chunk}"
                    all_chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "document": doc_title,
                            "section": section["title"],
                            "type": "text",
                            "chunk_index": i
                        }
                    })
            
            # 处理代码块
            for i, code_block in enumerate(section["code_blocks"]):
                code_text = section_context + f"代码语言: {code_block['language']}\n代码: {code_block['content']}"
                all_chunks.append({
                    "text": code_text,
                    "metadata": {
                        "document": doc_title,
                        "section": section["title"],
                        "type": "code",
                        "language": code_block['language']
                    }
                })
        
        return all_chunks

def build_vector_db():
    """构建向量数据库"""
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="sql_knowledge")
    
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    
    chunker = MarkdownChunker(chunk_size=600, chunk_overlap=50)
    
    markdown_files = [
        "knowledge/mysql/explain.md",
        "knowledge/mysql/index.md",
        "knowledge/mysql/pagination.md",
        "knowledge/mysql/join.md",
        "knowledge/mysql/optimization.md",
        "knowledge/blogs/slow_sql.md",
        "knowledge/blogs/filesort.md",
        "knowledge/blogs/index_fail.md"
    ]
    
    json_files = [
        "knowledge/query_rules.json",
        "knowledge/index_rules.json",
        "knowledge/explain_rules.json",
        "knowledge/optimization_cases.json",
        "knowledge/big_company_sql_standards.json"
    ]
    
    all_docs = []
    all_ids = []
    all_metas = []
    
    # 处理JSON文件
    print("Processing JSON files...")
    for filepath in json_files:
        if os.path.exists(filepath):
            print(f"  {filepath}")
            docs, ids = process_json_file(filepath)
            for doc, id_str in zip(docs, ids):
                all_docs.append(doc)
                all_ids.append(f"json_{id_str}")
                all_metas.append({"type": "json", "source": filepath})
    
    # 处理Markdown文件
    print("\nProcessing Markdown files...")
    for filepath in markdown_files:
        if os.path.exists(filepath):
            print(f"  {filepath}")
            chunks = chunker.chunk_markdown(filepath)
            doc_title = os.path.basename(filepath).replace('.md', '')
            for i, chunk in enumerate(chunks):
                all_docs.append(chunk["text"])
                all_ids.append(f"md_{doc_title}_{i}")
                all_metas.append(chunk["metadata"])
    
    # 写入向量数据库
    if all_docs:
        print(f"\nWriting {len(all_docs)} chunks to ChromaDB...")
        collection.add(
            ids=all_ids,
            documents=all_docs,
            metadatas=all_metas
        )
        print("✅ Done!")
    else:
        print("❌ No files found")

def process_json_file(filepath):
    """处理JSON文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    docs = []
    ids = []
    
    if "rules" in data:
        for rule in data["rules"]:
            text = f"规则ID: {rule.get('rule_id', '')}\n标题: {rule.get('title', '')}\n标准: {rule.get('standard', '')}\n问题: {rule.get('problem', '')}\n原因: {rule.get('reason', '')}\n解决方案: {rule.get('solution', '')}\n示例: {rule.get('example', '')}\n来源: {rule.get('source', '')}"
            docs.append(text)
            ids.append(rule.get('rule_id', str(len(ids))))
    
    elif "cases" in data:
        for case in data["cases"]:
            text = f"案例ID: {case.get('case_id', '')}\n标题: {case.get('title', '')}\n问题: {case.get('problem', '')}\n原始SQL: {case.get('original_sql', '')}\n分析: {case.get('problem_analysis', '')}\n优化方案: {case.get('optimization_plan', '')}\n优化后SQL: {case.get('optimized_sql', '')}"
            docs.append(text)
            ids.append(case.get('case_id', str(len(ids))))
    
    elif "sections" in data:
        for section in data["sections"]:
            category = section.get("category", "")
            for rule in section.get("rules", []):
                text = f"分类: {category}\n规则ID: {rule.get('rule_id', '')}\n标题: {rule.get('title', '')}\n标准: {rule.get('standard', '')}\n示例: {rule.get('example', '')}"
                docs.append(text)
                ids.append(f"bc_{rule.get('rule_id', str(len(ids)))}")
    
    return docs, ids

if __name__ == "__main__":
    build_vector_db()
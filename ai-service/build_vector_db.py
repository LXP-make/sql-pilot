import json
import os
import re
import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = "./knowledge"
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "sql_rules"
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
CHUNK_SIZE = 500


def load_md_file(filepath: str) -> list[dict]:
    """Load a markdown file, split into sections by headings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    rel_path = os.path.relpath(filepath, KNOWLEDGE_DIR)
    sections = re.split(r"(?=^#{1,3}\s)", content, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section or len(section) < 50:
            continue
        heading = section.split("\n")[0][:100] if section.split("\n") else ""
        chunks.append({
            "id": f"md:{rel_path}:{heading[:50]}",
            "text": section[:CHUNK_SIZE],
            "metadata": {
                "source": rel_path,
                "type": "markdown",
                "heading": heading,
            },
        })
    return chunks


def load_json_rules(filepath: str) -> list[dict]:
    """Load structured JSON knowledge files."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rel_path = os.path.relpath(filepath, KNOWLEDGE_DIR)
    chunks = []
    doc_id = data.get("document_id", "")

    for key in ("rules", "cases"):
        entries = data.get(key, [])
        for entry in entries:
            title = entry.get("title", "") or entry.get("case_id", "")
            problem = entry.get("problem", "") or entry.get("problem_analysis", "")
            reason = entry.get("reason", "")
            solution = entry.get("solution", "") or entry.get("optimization_plan", "")
            example = entry.get("good_example", "") or entry.get("optimized_sql", "")
            bad_example = entry.get("bad_example", "") or entry.get("original_sql", "")

            text = f"【{title}】\n问题: {problem}\n原因: {reason}\n方案: {solution}\n"
            if good_example := entry.get("good_example"):
                text += f"推荐写法: {good_example}\n"
            if bad_example:
                text += f"错误写法: {bad_example}\n"
            if source := entry.get("source"):
                text += f"来源: {source}\n"

            chunks.append({
                "id": f"json:{rel_path}:{entry.get('rule_id') or entry.get('case_id') or title}",
                "text": text[:CHUNK_SIZE],
                "metadata": {
                    "source": rel_path,
                    "type": "json_rule",
                    "title": title,
                    "doc_id": doc_id,
                },
            })

    if not chunks:
        chunks.append({
            "id": f"json:{rel_path}:full",
            "text": json.dumps(data, ensure_ascii=False)[:CHUNK_SIZE],
            "metadata": {"source": rel_path, "type": "json_raw"},
        })

    return chunks


def load_big_company_standards(filepath: str) -> list[dict]:
    """Load big_company_sql_standards.json — extracts each rule from sections as a chunk."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rel_path = os.path.relpath(filepath, KNOWLEDGE_DIR)
    chunks = []

    for section in data.get("sections", []):
        category = section.get("category", "")
        company = section.get("company", "")
        for entry in section.get("rules", []):
            title = entry.get("title", "")
            standard = entry.get("standard", "")
            bad_example = entry.get("bad_example", "")
            good_example = entry.get("good_example", "")
            example = entry.get("example", "")
            source = entry.get("source", "")

            text = f"[{category}]\n【{title}】\n规范: {standard}\n"
            if good_example:
                text += f"推荐写法: {good_example}\n"
            if bad_example:
                text += f"错误写法: {bad_example}\n"
            if example:
                text += f"示例: {example}\n"
            if source:
                text += f"来源: {source}\n"

            chunks.append({
                "id": f"json:{rel_path}:{entry.get('rule_id', '') or title}",
                "text": text[:CHUNK_SIZE],
                "metadata": {
                    "source": rel_path,
                    "type": "json_standard",
                    "category": category[:100],
                    "company": company or "General",
                    "title": title,
                },
            })

    if not chunks:
        # fallback: recursive walk for other JSON structures
        def walk(obj, path_str: str, depth: int = 0):
            if depth > 3:
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str) and len(v) > 30:
                        chunks.append({
                            "id": f"json:{rel_path}:{path_str}.{k}"[:200],
                            "text": v[:CHUNK_SIZE],
                            "metadata": {"source": rel_path, "type": "json_standard", "section": f"{path_str}.{k}"},
                        })
                    else:
                        walk(v, f"{path_str}.{k}", depth + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, str) and len(item) > 30:
                        chunks.append({
                            "id": f"json:{rel_path}:{path_str}[{i}]"[:200],
                            "text": item[:CHUNK_SIZE],
                            "metadata": {"source": rel_path, "type": "json_standard", "section": f"{path_str}[{i}]"},
                        })
                    else:
                        walk(item, f"{path_str}[{i}]", depth + 1)
        walk(data, "root")

    return chunks


def build_knowledge_base() -> list[dict]:
    """Load all knowledge sources and return list of document chunks."""
    all_chunks = []
    loaders = {
        ".md": load_md_file,
    }

    json_handlers = {
        "query_rules.json": load_json_rules,
        "index_rules.json": load_json_rules,
        "explain_rules.json": load_json_rules,
        "optimization_cases.json": load_json_rules,
        "big_company_sql_standards.json": load_big_company_standards,
    }

    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1]
            if ext == ".md":
                all_chunks.extend(load_md_file(filepath))
            elif filename in json_handlers:
                print(f"  Loading {filename}...")
                all_chunks.extend(json_handlers[filename](filepath))

    print(f"  Total chunks: {len(all_chunks)}")
    return all_chunks


def main():
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading knowledge base...")
    chunks = build_knowledge_base()

    if not chunks:
        print("No knowledge found!")
        return

    print(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print(f"Connecting to ChromaDB at {CHROMA_DB_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Clear existing data
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)

    collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    print(f"Done! Indexed {len(chunks)} chunks into ChromaDB collection '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()

"""Validated local file input; does not crawl arbitrary URLs."""
import json
from pathlib import Path


def read_documents(path: str | Path):
    path = Path(path)
    files = sorted(path.rglob("*")) if path.is_dir() else [path]
    found = 0
    for file in files:
        if not file.is_file() or file.suffix.lower() not in {".txt", ".md", ".jsonl"}:
            continue
        if file.suffix.lower() == ".jsonl":
            for i, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict) or not isinstance(item.get("text"), str):
                    raise ValueError(f"Invalid JSONL record: {file}:{i}")
                found += 1
                yield str(item.get("id", f"{file.stem}:{i}")), item["text"]
        else:
            found += 1
            yield file.relative_to(path).as_posix() if path.is_dir() else file.name, file.read_text(encoding="utf-8")
    if found == 0:
        raise ValueError("No supported documents found (.txt, .md, .jsonl)")

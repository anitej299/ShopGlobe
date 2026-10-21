"""Measured precision/recall over a fixed, manually curated judgment file."""
import json
import time
from pathlib import Path
from .keyword_search import search as keyword_search
from .semantic_search import search as semantic_search


def load_judgments(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if len(rows) < 30 or any(not r.get("relevant_ids") for r in rows):
        raise ValueError("At least 30 labeled queries are required")
    return rows


def evaluate(products, graph, path, k=10):
    rows = []
    for case in load_judgments(path):
        relevant = set(case["relevant_ids"])
        for method, engine in (("Keyword", lambda: keyword_search(case["query"], products, k)), ("Semantic", lambda: semantic_search(case["query"], products, graph, k)[0])):
            start = time.perf_counter()
            found = engine()
            elapsed = (time.perf_counter()-start)*1000
            ids = [r["product"]["id"] for r in found]
            hits = relevant.intersection(ids)
            rows.append({"query": case["query"], "method": method, "precision_at_k": len(hits)/k, "recall_at_k": len(hits)/len(relevant), "time_ms": elapsed, "hits": len(hits), "result_ids": ids, "relevant_ids": sorted(relevant)})
    return rows

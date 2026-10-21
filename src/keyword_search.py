"""A deliberately simple literal keyword baseline for evaluation."""
import re


def search(query, products, limit=20):
    terms = set(re.findall(r"[a-z0-9]+", query.casefold())) - {"for", "with", "the", "and", "under", "below", "in", "a", "an", "rs"}
    if not terms:
        return []
    results = []
    for p in products:
        hay = " ".join([p["name"], p["brand"], p["category"], p["description"]] + p["features"] + p["usage"]).casefold()
        count = sum(bool(re.search(r"\b" + re.escape(term) + r"\b", hay)) for term in terms)
        if count:
            results.append({"product": p, "score": round(100 * count / len(terms), 1), "explanation": [f"{count} literal keyword matches"]})
    return sorted(results, key=lambda x: (-x["score"], -x["product"]["rating"]))[:limit]

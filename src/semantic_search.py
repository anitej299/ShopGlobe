"""SPARQL candidate retrieval followed by strict attribute filtering and ranking."""
from .query_processor import parse_query
from .recommendation_engine import rank_product
from .sparql_engine import find_product_ids


def search(query, products, graph, limit=20):
    intent = parse_query(query)
    if not intent.raw:
        return [], intent
    ids = find_product_ids(graph, intent.category, intent.max_price)
    ranked = [result for p in products if p["id"] in ids if (result := rank_product(p, intent)) is not None]
    ranked.sort(key=lambda row: (-row["score"], -row["product"]["rating"], row["product"]["price"]))
    return ranked[:limit], intent

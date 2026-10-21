from pathlib import Path
import pytest
from src.xml_parser import parse_xml
from src.data_cleaner import clean_products
from src.rdf_graph import build_graph
from src.query_processor import parse_query
from src.semantic_search import search

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS, _ = clean_products(parse_xml(ROOT / "data/products.xml"))
GRAPH = build_graph(PRODUCTS)


def test_flat_feet_expansion_and_price():
    rows, intent = search("Waterproof running shoes for flat feet under ₹5,000", PRODUCTS, GRAPH)
    assert intent.category == "Running Shoes"
    assert rows
    assert all(r["product"]["price"] <= 5000 and r["product"]["attributes"]["waterproof"] == "true" and r["product"]["attributes"]["stability_support"] == "true" for r in rows)


def test_laptop_ram_and_price():
    rows, _ = search("Gaming laptop with 16GB RAM below ₹70,000", PRODUCTS, GRAPH)
    assert rows
    assert all(r["product"]["price"] <= 70000 and int(r["product"]["specifications"]["ram_gb"]) >= 16 for r in rows)


def test_empty_and_invalid():
    assert search("", PRODUCTS, GRAPH)[0] == []
    assert search("waterproof laptop under 1", PRODUCTS, GRAPH)[0] == []
    with pytest.raises(ValueError):
        parse_query(None)
    with pytest.raises(ValueError):
        parse_query("x" * 501)

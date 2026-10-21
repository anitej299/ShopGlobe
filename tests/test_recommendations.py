from pathlib import Path
from src.xml_parser import parse_xml
from src.data_cleaner import clean_products
from src.query_processor import parse_query
from src.recommendation_engine import rank_product

ROOT = Path(__file__).resolve().parents[1]


def test_mandatory_features_and_scoring():
    products, _ = clean_products(parse_xml(ROOT / "data/products.xml"))
    supported = next(p for p in products if p["category"] == "Running Shoes" and p["attributes"]["waterproof"] == "true" and p["attributes"]["stability_support"] == "true" and p["price"] <= 5000)
    intent = parse_query("waterproof running shoes for flat feet under 5000")
    result = rank_product(supported, intent)
    assert result is not None and 0 <= result["score"] <= 100
    assert any("stability support" in reason for reason in result["explanation"])
    unsupported = next(p for p in products if p["category"] == "Running Shoes" and p["attributes"]["waterproof"] == "false")
    assert rank_product(unsupported, intent) is None

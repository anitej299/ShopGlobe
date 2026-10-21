from pathlib import Path
from src.xml_parser import parse_xml
from src.data_cleaner import clean_products
from src.data_validator import validate_xml

ROOT = Path(__file__).resolve().parents[1]


def test_cleaned_xsd_and_report():
    valid, errors = validate_xml(ROOT / "data/cleaned_products.xml", ROOT / "data/products.xsd")
    assert valid, errors
    clean, report = clean_products(parse_xml(ROOT / "data/products.xml"))
    assert len(clean) >= 500
    assert report["duplicate_records"] >= 2
    assert report["missing_values"]["name"] >= 1
    assert report["invalid_records"] >= 3
    assert any("normalized category" in x for x in report["cleaning_actions"])


def test_raw_xsd_rejects_invalid_values():
    valid, _ = validate_xml(ROOT / "data/products.xml", ROOT / "data/products.xsd")
    assert not valid

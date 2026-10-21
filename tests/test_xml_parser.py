import pytest
from lxml import etree
from src.xml_parser import parse_xml, write_xml
from pathlib import Path

WORK = Path(__file__).resolve().parent


def test_roundtrip():
    product = {"id":"T1", "name":"Test", "brand":"B", "category":"Backpacks", "subcategory":"Campus", "description":"Sample", "price":1000, "rating":4.5, "stock":True, "features":["lightweight"], "usage":["college"], "specifications":{"weight_g":"500"}, "attributes":{"material":"mesh"}}
    path = WORK / "test_roundtrip.xml"
    try:
        write_xml([product], path)
        parsed = parse_xml(path)
        assert parsed[0]["name"] == "Test"
        assert parsed[0]["stock"] == "true"
    finally:
        path.unlink(missing_ok=True)


def test_malformed_xml():
    path = WORK / "test_broken.xml"
    try:
        path.write_text("<products><product>", encoding="utf-8")
        with pytest.raises(etree.XMLSyntaxError):
            parse_xml(path)
    finally:
        path.unlink(missing_ok=True)

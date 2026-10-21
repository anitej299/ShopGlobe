"""XSD and business-rule validation."""
from lxml import etree

CATEGORIES = {"Running Shoes", "Casual Shoes", "Sportswear", "Smartphones", "Laptops", "Headphones", "Smartwatches", "Backpacks", "Fitness Equipment", "Home Appliances"}


def validate_xml(xml_path, xsd_path):
    schema = etree.XMLSchema(etree.parse(str(xsd_path)))
    try:
        doc = etree.parse(str(xml_path), etree.XMLParser(resolve_entities=False, no_network=True))
        return schema.validate(doc), [str(e) for e in schema.error_log]
    except etree.XMLSyntaxError as exc:
        return False, [str(exc)]


def validate_product(p):
    problems = []
    for field in ("id", "name", "brand", "category", "subcategory"):
        if not str(p.get(field, "")).strip():
            problems.append(f"missing {field}")
    if p.get("category") not in CATEGORIES:
        problems.append("unknown category")
    try:
        if float(p["price"]) <= 0:
            problems.append("invalid price")
    except (ValueError, TypeError, KeyError):
        problems.append("invalid price")
    try:
        if not 0 <= float(p["rating"]) <= 5:
            problems.append("invalid rating")
    except (ValueError, TypeError, KeyError):
        problems.append("invalid rating")
    if p.get("stock") not in ("true", "false"):
        problems.append("invalid stock")
    if not p.get("attributes"):
        problems.append("missing attributes")
    return problems

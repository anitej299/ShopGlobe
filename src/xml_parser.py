"""Safe XML import/export; no entity expansion or network lookup."""
from pathlib import Path
from lxml import etree

FIELDS = ("name", "brand", "category", "subcategory", "description", "price", "rating", "stock")


def parse_xml(path):
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    root = etree.parse(str(path), parser).getroot()
    if root.tag != "products":
        raise ValueError("Expected <products> root")
    out = []
    for node in root.findall("product"):
        p = {"id": node.get("id", "")}
        p.update({key: (node.findtext(key) or "").strip() for key in FIELDS})
        for parent, child, target in (("features", "feature", "features"), ("usage", "activity", "usage")):
            p[target] = [x.text.strip() for x in node.findall(f"{parent}/{child}") if x.text and x.text.strip()]
        for parent, child, target in (("specifications", "spec", "specifications"), ("attributes", "attribute", "attributes")):
            p[target] = {x.get("key", ""): (x.text or "").strip() for x in node.findall(f"{parent}/{child}") if x.get("key")}
        out.append(p)
    return out


def write_xml(products, path):
    root = etree.Element("products", synthetic="true")
    for p in products:
        node = etree.SubElement(root, "product", id=str(p.get("id", "")))
        for field in FIELDS:
            value = p.get(field, "")
            etree.SubElement(node, field).text = str(value).lower() if isinstance(value, bool) else str(value)
        for parent, child, source in (("features", "feature", "features"), ("usage", "activity", "usage")):
            group = etree.SubElement(node, parent)
            for value in p.get(source, []):
                etree.SubElement(group, child).text = str(value)
        for parent, child, source in (("specifications", "spec", "specifications"), ("attributes", "attribute", "attributes")):
            group = etree.SubElement(node, parent)
            for key, value in p.get(source, {}).items():
                etree.SubElement(group, child, key=str(key)).text = str(value)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    etree.ElementTree(root).write(str(path), encoding="utf-8", xml_declaration=True, pretty_print=True)

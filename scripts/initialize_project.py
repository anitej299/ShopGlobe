"""Recreate all synthetic data, quality artifacts, ontology and knowledge graph."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_generator import generate_raw
from src.xml_parser import parse_xml, write_xml
from src.data_validator import validate_xml
from src.data_cleaner import clean_products
from src.rdf_graph import build_graph
from src.ontology_builder import build_ontology


def main():
    raw = ROOT / "data/products.xml"
    invalid = ROOT / "data/invalid_samples.xml"
    cleaned = ROOT / "data/cleaned_products.xml"
    generate_raw(raw, invalid)
    products = parse_xml(raw)
    clean, report = clean_products(products)
    write_xml(clean, cleaned)
    valid, errors = validate_xml(cleaned, ROOT / "data/products.xsd")
    if not valid:
        raise RuntimeError("Cleaned dataset failed XSD: " + "; ".join(errors))
    (ROOT / "data/quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "ontology").mkdir(parents=True, exist_ok=True)
    build_ontology().serialize(ROOT / "ontology/shopglobe.owl", format="xml")
    graph = build_graph(clean)
    graph.serialize(ROOT / "ontology/products.ttl", format="turtle")
    graph.serialize(ROOT / "ontology/products.rdf", format="xml")
    print(f"Raw: {len(products)}, cleaned: {len(clean)}, rejected: {len(report['rejected_records'])}, triples: {len(graph)}")


if __name__ == "__main__":
    main()

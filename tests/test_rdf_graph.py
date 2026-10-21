from pathlib import Path
from rdflib import RDF, RDFS
from src.xml_parser import parse_xml
from src.data_cleaner import clean_products
from src.rdf_graph import build_graph
from src.ontology_builder import SG
from src.sparql_engine import find_product_ids

ROOT = Path(__file__).resolve().parents[1]


def test_triples_and_sparql():
    products, _ = clean_products(parse_xml(ROOT / "data/products.xml"))
    graph = build_graph(products)
    assert (SG.RunningShoes, RDFS.subClassOf, SG.Footwear) in graph
    assert (SG["product/SG-0001"], RDF.type, SG.RunningShoes) in graph
    ids = find_product_ids(graph, "Running Shoes", 5000)
    assert ids
    assert all(next(p for p in products if p["id"] == i)["price"] <= 5000 for i in ids)

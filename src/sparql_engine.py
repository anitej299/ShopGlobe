"""Parameterized SPARQL discovery; hard limits are applied again during ranking."""
from rdflib import Literal, XSD
from .ontology_builder import SG


def find_product_ids(graph, category=None, max_price=None):
    category_clause = "?p sg:belongsToCategory ?wanted ." if category else ""
    query = f"""PREFIX sg: <https://example.org/shopglobe/>
    SELECT DISTINCT ?id WHERE {{ ?p sg:productId ?id ; sg:hasPrice ?price .
    {category_clause}
    FILTER (?price <= ?limit)
    }}"""
    bindings = {"limit": Literal(float(max_price) if max_price is not None else 1e12, datatype=XSD.decimal)}
    if category:
        from .rdf_graph import slug
        bindings["wanted"] = SG["category/" + slug(category)]
    return {str(row.id) for row in graph.query(query, initBindings=bindings)}

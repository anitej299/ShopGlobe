"""Explicit RDFS/OWL schema and documented related concepts."""
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal

SG = Namespace("https://example.org/shopglobe/")


def build_ontology():
    g = Graph()
    g.bind("sg", SG)
    g.bind("owl", OWL)
    for name in ("Product", "Footwear", "RunningShoes", "Electronics", "Smartphone", "Laptop", "Feature", "Brand", "Category", "Activity"):
        g.add((SG[name], RDF.type, OWL.Class))
    for child, parent in (("Footwear", "Product"), ("RunningShoes", "Footwear"), ("Electronics", "Product"), ("Smartphone", "Electronics"), ("Laptop", "Electronics")):
        g.add((SG[child], RDFS.subClassOf, SG[parent]))
    for prop in ("belongsToCategory", "hasFeature", "manufacturedBy", "suitableForActivity", "hasSupportType", "hasWaterResistance", "hasPrice", "hasRating", "hasStock", "hasRamGB", "relatedTo"):
        g.add((SG[prop], RDF.type, OWL.ObjectProperty if prop not in ("hasPrice", "hasRating", "hasStock", "hasRamGB") else OWL.DatatypeProperty))
    for a, b in (("StabilitySupport", "FlatFeetSupport"), ("Waterproof", "WaterResistance"), ("NoiseCancellation", "ANC")):
        g.add((SG[a], SG.relatedTo, SG[b]))
        g.add((SG[b], SG.relatedTo, SG[a]))
    g.add((SG.Product, RDFS.label, Literal("Synthetic catalog product")))
    return g

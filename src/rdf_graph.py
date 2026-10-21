"""Turn verified product attributes into RDF triples."""
from rdflib import URIRef, Literal, RDF, XSD
from .ontology_builder import SG, build_ontology


def slug(value):
    return "".join(ch if ch.isalnum() else "_" for ch in str(value)).strip("_")


def build_graph(products):
    g = build_ontology()
    classes = {"Running Shoes": SG.RunningShoes, "Casual Shoes": SG.Footwear, "Smartphones": SG.Smartphone, "Laptops": SG.Laptop, "Headphones": SG.Electronics, "Smartwatches": SG.Electronics}
    for p in products:
        subject = SG["product/" + p["id"]]
        g.add((subject, RDF.type, classes.get(p["category"], SG.Product)))
        g.add((subject, SG.productId, Literal(p["id"])))
        g.add((subject, SG.name, Literal(p["name"])))
        g.add((subject, SG.hasPrice, Literal(p["price"], datatype=XSD.decimal)))
        g.add((subject, SG.hasRating, Literal(p["rating"], datatype=XSD.decimal)))
        g.add((subject, SG.hasStock, Literal(p["stock"], datatype=XSD.boolean)))
        category = SG["category/" + slug(p["category"])]
        brand = SG["brand/" + slug(p["brand"])]
        g.add((subject, SG.belongsToCategory, category))
        g.add((subject, SG.manufacturedBy, brand))
        g.add((category, RDF.type, SG.Category))
        g.add((brand, RDF.type, SG.Brand))
        for feature in p["features"]:
            f = SG["feature/" + slug(feature)]
            g.add((subject, SG.hasFeature, f))
            g.add((f, RDF.type, SG.Feature))
        for activity in p["usage"]:
            a = SG["activity/" + slug(activity)]
            g.add((subject, SG.suitableForActivity, a))
            g.add((a, RDF.type, SG.Activity))
        if p["attributes"].get("waterproof") == "true":
            g.add((subject, SG.hasWaterResistance, SG.Waterproof))
        if p["attributes"].get("stability_support") == "true":
            g.add((subject, SG.hasSupportType, SG.StabilitySupport))
        if p["specifications"].get("ram_gb"):
            g.add((subject, SG.hasRamGB, Literal(int(p["specifications"]["ram_gb"]), datatype=XSD.integer)))
    return g

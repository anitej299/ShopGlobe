"""Small focused PyVis subgraph; never render all products."""
import streamlit.components.v1 as components
from pyvis.network import Network


def render_product_graph(product):
    net = Network(height="530px", width="100%", bgcolor="#ffffff", font_color="#102a43", directed=True)
    net.add_node(product["id"], label=product["name"], color="#0e9f9a", size=30, title=product["description"])
    links = [("Category", product["category"], "belongsToCategory"), ("Brand", product["brand"], "manufacturedBy")]
    links += [("Feature", f, "hasFeature") for f in product["features"]]
    links += [("Activity", a, "suitableForActivity") for a in product["usage"]]
    for kind, value, relation in links:
        key = kind + ":" + value
        net.add_node(key, label=value, color={"Category":"#174a72", "Brand":"#4f78a7", "Feature":"#f6b94c", "Activity":"#9a73bf"}[kind], title=kind)
        net.add_edge(product["id"], key, title=relation, label=relation)
    net.toggle_physics(False)
    components.html(net.generate_html(), height=550, scrolling=False)

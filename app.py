"""Streamlit Community Cloud entry point."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from rdflib import Graph
from src.xml_parser import parse_xml
from src.data_cleaner import clean_products
from src.analytics import summary
from src.semantic_search import search as semantic_search
from src.keyword_search import search as keyword_search
from src.evaluation import evaluate
from components.product_cards import product_card
from components.search_filters import filters
from components.knowledge_graph import render_product_graph
from components.dashboard_charts import charts

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="ShopGlobe", page_icon="🌐", layout="wide")
st.markdown("""<style>.stApp{background:#fff;color:#102a43}.block-container{max-width:1350px;padding-top:2rem}h1,h2,h3{color:#102a43}div[data-testid='stMetric']{background:#edf7f7;border-radius:12px;padding:12px}</style>""", unsafe_allow_html=True)


@st.cache_resource
def load_data():
    products, report = clean_products(parse_xml(ROOT / "data/products.xml"))
    graph = Graph().parse(ROOT / "ontology/products.ttl", format="turtle")
    return products, report, graph


try:
    products, report, graph = load_data()
except Exception as exc:
    st.error(f"Project data could not be loaded: {exc}. Run python scripts/initialize_project.py.")
    st.stop()

page = st.sidebar.radio("Explore", ["Home", "Intelligent Product Search", "Product Comparison", "Semantic Knowledge Graph", "Data Quality Dashboard", "Search Evaluation"])
st.sidebar.caption("Synthetic catalog · no purchases or external API")

if page == "Home":
    st.title("🌐 ShopGlobe")
    st.subheader("Find products by what they do")
    st.write("Search a synthetic catalog with XML, RDF, SPARQL and explainable rules.")
    query = st.text_input("What are you looking for?", placeholder="Waterproof running shoes for flat feet under ₹5,000")
    if query:
        try:
            rows, _ = semantic_search(query, products, graph, 6)
            st.session_state["query"] = query
            for row in rows:
                product_card(row)
            if not rows:
                st.info("No products meet every explicit requirement. Try changing a constraint.")
        except ValueError as exc:
            st.warning(str(exc))
    s = summary(products)
    cols = st.columns(4)
    for col, (label, value) in zip(cols, (("Products", s["count"]), ("Categories", s["categories"]), ("Brands", s["brands"]), ("In stock", s["in_stock"]))):
        col.metric(label, value)
    st.markdown("### Featured categories")
    st.write(" · ".join(sorted({p["category"] for p in products})))
    st.markdown("### Try a search")
    st.write("Waterproof running shoes for flat feet under ₹5,000 · Gaming laptop with 16GB RAM below ₹70,000 · Wireless headphones with noise cancellation")
    st.markdown("### Popular products")
    for p in sorted(products, key=lambda x: -x["rating"])[:3]:
        product_card({"product": p, "score": round(p["rating"]*20, 1), "explanation": ["Featured by catalog rating"]})

elif page == "Intelligent Product Search":
    st.title("Intelligent Product Search")
    query = st.text_input("Describe your ideal product", value=st.session_state.get("query", ""))
    accept, sort = filters(products)
    if query:
        try:
            with st.spinner("Searching the knowledge graph"):
                rows, intent = semantic_search(query, products, graph, len(products))
            rows = [r for r in rows if accept(r)]
            if sort == "Price: low to high": rows.sort(key=lambda r: r["product"]["price"])
            elif sort == "Price: high to low": rows.sort(key=lambda r: -r["product"]["price"])
            elif sort == "Rating": rows.sort(key=lambda r: -r["product"]["rating"])
            st.caption(f"{len(rows)} matches · Parsed category: {intent.category or 'any'} · Required features: {', '.join(intent.features) or 'none'} · Maximum: {intent.max_price or 'none'}")
            for row in rows[:40]: product_card(row)
            if len(rows) > 40: st.caption("Showing the first 40 matching products.")
            if not rows: st.info("No products meet every explicit requirement. Relax a filter or try another query.")
        except ValueError as exc:
            st.warning(str(exc))

elif page == "Product Comparison":
    st.title("Product Comparison")
    lookup = {f"{p['name']} ({p['id']})": p for p in products}
    selected = st.multiselect("Select 2–4 products", list(lookup), max_selections=4)
    if len(selected) >= 2:
        query = st.text_input("Optional query for relevance", key="comparison_query")
        scores = {}
        if query:
            try:
                scores = {r["product"]["id"]: r["score"] for r in semantic_search(query, products, graph, len(products))[0]}
            except ValueError as exc:
                st.warning(str(exc))
        records = []
        for name in selected:
            p = lookup[name]
            records.append({"Product": p["name"], "Price ₹": p["price"], "Rating": p["rating"], "Category": p["category"], "Features": ", ".join(p["features"]), "Specifications": ", ".join(f"{k}: {v}" for k,v in p["specifications"].items()), "Usage": ", ".join(p["usage"]), "Search relevance": scores.get(p["id"], "Does not meet query" if query else "—")})
        st.dataframe(pd.DataFrame(records).set_index("Product").T, use_container_width=True)
        st.caption("Lowest price: " + min(records, key=lambda r:r["Price ₹"])["Product"] + " · Highest rating: " + max(records, key=lambda r:r["Rating"])["Product"])
    else: st.info("Choose at least two products to compare.")

elif page == "Semantic Knowledge Graph":
    st.title("Semantic Knowledge Graph")
    category = st.selectbox("Filter category", sorted({p["category"] for p in products}))
    subset = [p for p in products if p["category"] == category]
    p = st.selectbox("Inspect product", subset, format_func=lambda x:f"{x['name']} ({x['id']})")
    render_product_graph(p)
    st.caption("Edges show the relationships stored in RDF. Related concepts are explicit ontology links; this view does not imply full OWL reasoning.")

elif page == "Data Quality Dashboard":
    st.title("Data Quality Dashboard")
    st.caption("Deterministic synthetic source; rejected records are preserved in invalid_samples.xml.")
    cols = st.columns(4)
    for col, (label, value) in zip(cols, (("Raw", report["total_raw_products"]), ("Usable", report["final_usable_products"]), ("Invalid", report["invalid_records"]), ("Duplicates", report["duplicate_records"]))): col.metric(label, value)
    st.write("Missing values by field:", report["missing_values"])
    st.write("Cleaning actions:", report["cleaning_actions"])
    st.dataframe(pd.DataFrame(report["rejected_records"]), use_container_width=True)
    charts(products)
    st.plotly_chart(px.bar(x=["Raw", "After cleaning"], y=[report["total_raw_products"], report["final_usable_products"]], labels={"x":"Stage", "y":"Records"}, title="Data quality: record counts"), use_container_width=True)
    st.caption("The two bars show pipeline stages for one dataset, not a time series.")

elif page == "Search Evaluation":
    st.title("Search Evaluation")
    st.write("A fixed set of curated relevance judgments compares the literal keyword baseline with ShopGlobe. Results below are measured when this page runs.")
    k = st.slider("K", 1, 20, 10)
    if st.button("Run evaluation"):
        with st.spinner("Measuring both search methods"):
            results = evaluate(products, graph, ROOT / "data/evaluation_queries.json", k)
        df = pd.DataFrame(results)
        st.dataframe(df[["query", "method", "precision_at_k", "recall_at_k", "time_ms", "hits", "result_ids"]], use_container_width=True)
        means = df.groupby("method")[["precision_at_k", "recall_at_k", "time_ms"]].mean().reset_index()
        st.plotly_chart(px.bar(means, x="method", y=["precision_at_k", "recall_at_k"], barmode="group", title=f"Mean precision and recall at {k}"), use_container_width=True)
        st.plotly_chart(px.bar(means, x="method", y="time_ms", title="Mean measured query time (ms)"), use_container_width=True)
        st.caption("Judgment lists cover known relevant examples, not every relevant catalog product; recall uses only the listed judgments. Processing times vary by machine and cache state.")
    st.markdown("### Compare one query")
    judgments = json.loads((ROOT / "data/evaluation_queries.json").read_text(encoding="utf-8"))
    example = st.selectbox("Labeled query", [case["query"] for case in judgments])
    if example:
        relevant = set(next(case["relevant_ids"] for case in judgments if case["query"] == example))
        left, right = st.columns(2)
        with left:
            st.subheader("Keyword")
            for row in keyword_search(example, products, 5):
                st.caption("Labeled relevant" if row["product"]["id"] in relevant else "Not in judgment list")
                product_card(row)
        with right:
            st.subheader("Semantic")
            for row in semantic_search(example, products, graph, 5)[0]:
                st.caption("Labeled relevant" if row["product"]["id"] in relevant else "Not in judgment list")
                product_card(row)
        st.caption("Not in judgment list means unjudged, not necessarily irrelevant.")

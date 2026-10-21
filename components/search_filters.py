import streamlit as st


def filters(products):
    categories = sorted({p["category"] for p in products})
    brands = sorted({p["brand"] for p in products})
    a, b, c = st.columns(3)
    category = a.selectbox("Category", ["All"] + categories)
    brand = b.selectbox("Brand", ["All"] + brands)
    max_price = c.number_input("Maximum price (₹)", 0, 200000, 0, step=500, help="0 means no extra limit")
    d, e, f = st.columns(3)
    rating = d.slider("Minimum rating", 0.0, 5.0, 0.0, .1)
    stock = e.checkbox("In stock only", value=True)
    sort = f.selectbox("Sort", ["Relevance", "Price: low to high", "Price: high to low", "Rating"])
    def accept(row):
        p = row["product"]
        return (category == "All" or p["category"] == category) and (brand == "All" or p["brand"] == brand) and (not max_price or p["price"] <= max_price) and p["rating"] >= rating and (not stock or p["stock"])
    return accept, sort

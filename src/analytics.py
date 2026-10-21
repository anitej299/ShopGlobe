"""Catalog summaries for dashboard and notebook."""
import pandas as pd


def product_frame(products):
    return pd.DataFrame([{k: p[k] for k in ("id", "name", "brand", "category", "price", "rating", "stock")} for p in products])


def summary(products):
    df = product_frame(products)
    return {"count": len(df), "categories": int(df.category.nunique()), "brands": int(df.brand.nunique()), "median_price": float(df.price.median()), "in_stock": int(df.stock.sum())}

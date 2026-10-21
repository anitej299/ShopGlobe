import plotly.express as px
import streamlit as st
from src.analytics import product_frame


def charts(products):
    df = product_frame(products)
    a, b = st.columns(2)
    a.plotly_chart(px.bar(df.category.value_counts().rename_axis("category").reset_index(name="products"), x="category", y="products", title="Category distribution", color_discrete_sequence=["#0e9f9a"]), use_container_width=True)
    b.plotly_chart(px.bar(df.brand.value_counts().head(12).rename_axis("brand").reset_index(name="products"), x="brand", y="products", title="Top brands", color_discrete_sequence=["#174a72"]), use_container_width=True)
    st.plotly_chart(px.histogram(df, x="price", color="category", nbins=35, title="Price distribution (INR)"), use_container_width=True)

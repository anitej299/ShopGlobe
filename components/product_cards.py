import streamlit as st


def product_card(row):
    p = row["product"]
    with st.container(border=True):
        st.markdown(f"#### {p['name']}")
        st.caption(f"{p['brand']} · {p['category']} · {'In stock' if p['stock'] else 'Out of stock'}")
        a, b, c = st.columns(3)
        a.metric("Price", f"₹{p['price']:,.0f}")
        b.metric("Rating", f"{p['rating']:.1f} / 5")
        c.metric("Match", f"{row['score']:.0f}%")
        st.write(" · ".join(p["features"]))
        st.caption("Why it matches: " + "; ".join(row["explanation"]))

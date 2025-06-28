# This version is designed to run in a general Python environment without Streamlit
# It reads an input file (CSV or Excel), performs best-fit pipe cutting, and outputs a summary Excel file

import streamlit as st

st.set_page_config(page_title="Pipe Cutting Optimizer", layout="centered")
st.title("🧮 Pipe Cutting Optimizer")

stock_length = st.number_input("🧱 Stock pipe length (m):", min_value=0.5, value=6.0, step=0.5)
input_str = st.text_area("✂️ Pipe lengths (comma separated)", "2.5, 3.1, 1.2, 2.8")

if st.button("🚀 Calculate"):
    try:
        lengths = list(map(float, input_str.split(",")))
        lengths.sort(reverse=True)

        result = []
        for length in lengths:
            placed = False
            for r in result:
                if sum(r) + length <= stock_length:
                    r.append(length)
                    placed = True
                    break
            if not placed:
                result.append([length])

        st.success(f"✅ Total pipes needed: {len(result)}")
        for i, group in enumerate(result, 1):
            used = sum(group)
            waste = stock_length - used
            st.write(f"Pipe {i}: {group} (Used: {used:.2f} / Waste: {waste:.2f} m)")

    except Exception as e:
        st.error(f"❌ Error: {e}")


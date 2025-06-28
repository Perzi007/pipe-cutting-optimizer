
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Pipe Cutting Optimizer", layout="centered")
st.title("🧮 Pipe Cutting Optimizer with Waste & Export")

stock_length = st.number_input("🧱 Stock pipe length (m):", min_value=0.5, value=6.0, step=0.5)
input_str = st.text_area("✂️ Pipe lengths to cut (comma separated)", "2.5, 3.1, 1.2, 2.8, 1.5, 3.0")

def best_fit_with_waste(needed_lengths, stock_length):
    needed_lengths.sort(reverse=True)
    stocks = []
    for length in needed_lengths:
        placed = False
        for stock in stocks:
            if sum(stock) + length <= stock_length:
                stock.append(length)
                placed = True
                break
        if not placed:
            stocks.append([length])
    results = []
    for i, stock in enumerate(stocks, 1):
        used = sum(stock)
        waste = stock_length - used
        results.append({
            "Pipe #": f"Pipe {i}",
            "Cut pieces": stock,
            "Used (m)": round(used, 2),
            "Waste (m)": round(waste, 2)
        })
    return results

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Pipe Summary")
    output.seek(0)
    return output

if st.button("🚀 Calculate"):
    try:
        lengths = list(map(float, input_str.split(",")))
        result = best_fit_with_waste(lengths, stock_length)
        df = pd.DataFrame(result)

        st.success(f"✅ Total pipes needed: {len(df)}")
        st.dataframe(df, use_container_width=True)

        # Export
        excel_data = convert_df_to_excel(df)
        st.download_button("📥 Download Excel", data=excel_data, file_name="pipe_cutting_result.xlsx")

    except Exception as e:
        st.error(f"❌ Error: {e}")

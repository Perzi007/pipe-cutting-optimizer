
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Pipe Cutting Optimizer", layout="centered")
st.title("🧮 Pipe Cutting Optimizer (Auto Split for Long Cuts)")

PIPE_LENGTH = st.number_input("🧱 Stock pipe length (m):", min_value=0.5, value=6.0, step=0.5)
input_str = st.text_area("✂️ Pipe lengths to cut (comma separated)", "3, 4, 5, 6, 9, 9, 12, 15, 15")

# แยกความยาวที่เกิน stock ออก
def split_long_lengths(lengths, pipe_len):
    result = []
    for length in lengths:
        while length > pipe_len:
            result.append(pipe_len)
            length -= pipe_len
        if length > 0:
            result.append(round(length, 2))
    return result

# Best Fit Strategy
def best_fit(cuts, pipe_len):
    cuts = sorted(cuts, reverse=True)
    bins = []
    for cut in cuts:
        best_idx = -1
        min_space = pipe_len + 1
        for i, b in enumerate(bins):
            space_left = b['remaining']
            if 0 <= space_left - cut < min_space:
                best_idx = i
                min_space = space_left - cut
        if best_idx >= 0:
            bins[best_idx]['cuts'].append(cut)
            bins[best_idx]['remaining'] -= cut
        else:
            bins.append({'cuts': [cut], 'remaining': pipe_len - cut})
    return bins

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Pipe Summary")
    output.seek(0)
    return output

if st.button("🚀 Calculate"):
    try:
        raw_lengths = list(map(float, input_str.split(",")))
        split_lengths = split_long_lengths(raw_lengths, PIPE_LENGTH)
        result = best_fit(split_lengths, PIPE_LENGTH)

        summary = []
        for i, b in enumerate(result, 1):
            used = round(PIPE_LENGTH - b['remaining'], 2)
            summary.append({
                "Pipe #": f"Pipe {i}",
                "Cut pieces": ", ".join(map(str, b['cuts'])),
                "Used (m)": used,
                "Waste (m)": round(b['remaining'], 2)
            })
        df = pd.DataFrame(summary)
        st.success(f"✅ Total pipes used: {len(df)}")
        st.dataframe(df, use_container_width=True)

        excel_data = convert_df_to_excel(df)
        st.download_button("📥 Download Excel", data=excel_data, file_name="pipe_cutting_result_testcase.xlsx")

    except Exception as e:
        st.error(f"❌ Error: {e}")

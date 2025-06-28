# This version is designed to run in a general Python environment without Streamlit
# It reads an input file (CSV or Excel), performs best-fit pipe cutting, and outputs a summary Excel file

import pandas as pd
from math import ceil
from pathlib import Path

PIPE_LENGTH = 6.0
INPUT_FILE = "cut_lengths.xlsx"  # Change to your input file name
OUTPUT_FILE = "pipe_cutting_summary.xlsx"

# Function to parse uploaded file
def parse_file(file_path):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, header=None)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path, header=None)
    else:
        raise ValueError("Unsupported file format.")
    cuts = df.values.flatten().tolist()
    return [float(c) for c in cuts if pd.notnull(c)]

# Split any length > 6m
def split_long_lengths(lengths):
    result = []
    for length in lengths:
        while length > PIPE_LENGTH:
            result.append(PIPE_LENGTH)
            length -= PIPE_LENGTH
        if length > 0:
            result.append(round(length, 2))
    return result

# Best Fit Strategy
def best_fit(cuts):
    cuts = sorted(cuts, reverse=True)
    bins = []
    for cut in cuts:
        placed = False
        best_idx = -1
        min_space = PIPE_LENGTH + 1
        for i, bin in enumerate(bins):
            if 0 <= bin['remaining'] - cut < min_space:
                best_idx = i
                min_space = bin['remaining'] - cut
        if best_idx >= 0:
            bins[best_idx]['cuts'].append(cut)
            bins[best_idx]['remaining'] -= cut
        else:
            bins.append({'cuts': [cut], 'remaining': PIPE_LENGTH - cut})
    return bins

# Main execution
if __name__ == "__main__":
    if not Path(INPUT_FILE).exists():
        print(f"Input file '{INPUT_FILE}' not found.")
    else:
        raw_cuts = parse_file(INPUT_FILE)
        preprocessed = split_long_lengths(raw_cuts)
        results = best_fit(preprocessed)

        print(f"✅ Minimum pipes required: {len(results)}")
        print(f"♻️ Total scrap length: {round(sum(r['remaining'] for r in results), 2)} meters")

        df_summary = pd.DataFrame([
            {"Pipe #": i+1, "Used Length (m)": round(PIPE_LENGTH - r['remaining'], 2),
             "Scrap (m)": round(r['remaining'], 2), "Cuts": ", ".join(map(str, r['cuts']))}
            for i, r in enumerate(results)
        ])

        with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
            df_summary.to_excel(writer, sheet_name='BestFitSummary', index=False)

        print(f"📁 Summary saved to '{OUTPUT_FILE}'")

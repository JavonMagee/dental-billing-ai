import pandas as pd
import os

def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, encoding="latin1", engine="python", on_bad_lines='skip')
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def find_column(columns, keywords):
    for col in columns:
        col_clean = col.lower().strip().replace(" ", "").replace("_", "")
        for keyword in keywords:
            if keyword in col_clean:
                return col
    return None

def analyze_and_flag(production_path, uncollected_path, output_path='temp/flagged_report.xlsx'):
    df_production = read_file(production_path)
    df_uncollected = read_file(uncollected_path)

    df_production.columns = df_production.columns.str.strip()
    df_uncollected.columns = df_uncollected.columns.str.strip()

    # Detect key columns
    prod_patient_col = find_column(df_production.columns, ["patientname", "ptname"])
    unc_patient_col = find_column(df_uncollected.columns, ["patientname", "ptname"])
    unc_balance_col = find_column(df_uncollected.columns, ["uncollected", "balance", "due", "owed"])

    if not prod_patient_col or not unc_patient_col or not unc_balance_col:
        raise KeyError(
            f"Missing required columns.\nProduction Columns: {df_production.columns.tolist()}\nUncollected Columns: {df_uncollected.columns.tolist()}"
        )

    # Normalize patient names
    df_production["__norm_name"] = df_production[prod_patient_col].astype(str).str.lower().str.strip()
    df_uncollected["__norm_name"] = df_uncollected[unc_patient_col].astype(str).str.lower().str.strip()

    # Sum uncollected values
    uncollected_summary = df_uncollected.groupby("__norm_name")[unc_balance_col].sum().reset_index()
    uncollected_summary.columns = ["__norm_name", "Total Uncollected"]
    flagged = uncollected_summary[uncollected_summary["Total Uncollected"] > 300]

    # Merge with normalized name
    df_merged = df_production.merge(flagged, how="left", on="__norm_name")
    df_merged["Balance Flag"] = df_merged["Total Uncollected"].apply(
        lambda x: f"Balance: ${x:.2f}" if pd.notnull(x) else ""
    )

    # Final report columns
    final_columns = ['Date', 'Patient Name', 'Description', 'Prov', 'Production',
                     'Adjust', 'Write-off', 'Pt Income', 'Ins Income', 'Balance Flag']
    df_final = df_merged[final_columns]

    # Save output
    os.makedirs("temp", exist_ok=True)
    df_final.to_excel(output_path, index=False)

    # Executive summary
    summary = f"{len(flagged)} patients flagged for balances over $300.\n"
    for _, row in flagged.iterrows():
        summary += f"- {row['__norm_name'].title()}: ${row['Total Uncollected']:.2f}\n"

    return summary, output_path







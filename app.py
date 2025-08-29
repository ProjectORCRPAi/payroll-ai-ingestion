import streamlit as st
import pandas as pd
from engine import load_and_process

st.set_page_config(page_title="Payroll AI Ingestion", page_icon="📄")
st.title("Payroll AI Ingestion Engine + Contribution Mapping")
st.caption("Upload a payroll CSV/XLSX, we’ll map & validate it, and give you a clean export.")

uploaded_file = st.file_uploader("Upload Payroll File (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        df = load_and_process(uploaded_file)
        st.success("✅ File processed! Preview below.")
        st.dataframe(df.head(100))

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Processed CSV", csv_bytes, "processed_payroll.csv", "text/csv")

        over = int(df.get("over_limit", []).sum()) if "over_limit" in df else 0
        capped = int(df.get("match_capped", []).sum()) if "match_capped" in df else 0
        st.write(f"**Over annual limit:** {over} rows | **Match capped:** {capped} rows")
    except Exception as e:
        st.error("""There was a problem reading your file. 
        Make sure it's a valid CSV or Excel and the first row is headers.""")
        st.exception(e)
else:
    st.info("Tip: Try the sample file from the repo: `samples/sample_paylocity.csv`.")

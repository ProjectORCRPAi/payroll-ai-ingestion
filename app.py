import streamlit as st
import pandas as pd
from engine import load_and_process

st.title("Payroll AI Ingestion Engine")

uploaded_file = st.file_uploader("Upload Payroll File (.csv or .xlsx)", type=["csv", "xlsx"])
if uploaded_file:
    df = load_and_process(uploaded_file)
    st.success("File processed!")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Processed File", csv, "processed_payroll.csv", "text/csv")

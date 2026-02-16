import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002")

st.set_page_config(page_title="Investment ETL Reporting", layout="wide")
st.title("Investment ETL + Reporting Dashboard")
st.caption("Upload portfolio price data, compute risk/return metrics, and generate an auto report.")

st.subheader("1) Upload CSV and run ETL")
uploaded_file = st.file_uploader(
    "CSV schema: date,ticker,close,shares",
    type=["csv"],
)

if st.button("Run ingestion", type="primary"):
    if uploaded_file is None:
        st.warning("Please upload a CSV file first.")
    else:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        try:
            response = requests.post(f"{API_BASE_URL}/ingest", files=files, timeout=60)
            if response.ok:
                result = response.json()
                st.success(
                    f"Run {result['run_id']} completed: {result['rows_loaded']} rows, {len(result['tickers'])} tickers."
                )
            else:
                st.error(response.text)
        except Exception as error:
            st.error(str(error))

st.subheader("2) View metrics summary")
run_id_input = st.text_input("Run ID (optional, leave empty for latest)")
if st.button("Load summary"):
    params = {}
    if run_id_input.strip():
        params["run_id"] = run_id_input.strip()

    try:
        response = requests.get(f"{API_BASE_URL}/metrics/summary", params=params, timeout=30)
        if response.ok:
            data = response.json()
            st.info(
                f"Run {data['run_id']} • Tickers: {data['ticker_count']} • Best return: {data['best_annualized_return']['ticker']}"
            )
            st.dataframe(data["metrics"], use_container_width=True)
        else:
            st.error(response.text)
    except Exception as error:
        st.error(str(error))

st.subheader("3) Generate report")
if st.button("Generate markdown report"):
    payload_params = {}
    if run_id_input.strip():
        payload_params["run_id"] = run_id_input.strip()

    try:
        response = requests.post(f"{API_BASE_URL}/report", params=payload_params, timeout=30)
        if response.ok:
            report = response.json()
            st.success(f"Report {report['report_id']} generated for run {report['run_id']}.")
            st.markdown(report["report_markdown"])
            st.download_button(
                "Download report",
                data=report["report_markdown"],
                file_name=f"investment_report_run_{report['run_id']}.md",
                mime="text/markdown",
            )
        else:
            st.error(response.text)
    except Exception as error:
        st.error(str(error))

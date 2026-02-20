import pandas as pd
import requests
import streamlit as st


API_BASE_URL = "http://api:8000"


st.set_page_config(page_title="sentiment-analysis-nlp", layout="wide")
st.title("Sentiment & Topic Analysis Dashboard")

st.write("Upload reviews, run analysis, and inspect sentiment + topic clusters.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file and st.button("Ingest dataset"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
    response = requests.post(f"{API_BASE_URL}/ingest", files=files, timeout=120)
    if response.ok:
        st.success(response.json())
    else:
        st.error(response.text)

st.divider()

topic_count = st.slider("Topic count", min_value=2, max_value=10, value=4)
if st.button("Run analysis"):
    response = requests.post(f"{API_BASE_URL}/analyze", json={"topic_count": topic_count}, timeout=240)
    if response.ok:
        st.success(response.json())
    else:
        st.error(response.text)

st.divider()

if st.button("Load latest results"):
    results_response = requests.get(f"{API_BASE_URL}/results", timeout=120)
    summary_response = requests.get(f"{API_BASE_URL}/summary", timeout=120)

    if results_response.ok:
        payload = results_response.json()
        data = pd.DataFrame(payload["records"])
        st.subheader(f"Run {payload['run_id']} results")

        if not data.empty:
            sentiment_counts = data["sentiment_label"].value_counts()
            st.bar_chart(sentiment_counts)

            topic_counts = data["topic_id"].value_counts().sort_index()
            st.bar_chart(topic_counts)

            st.dataframe(data)
        else:
            st.info("No records returned.")
    else:
        st.error(results_response.text)

    if summary_response.ok:
        st.subheader("Summary")
        st.write(summary_response.json()["summary_text"])
    else:
        st.error(summary_response.text)

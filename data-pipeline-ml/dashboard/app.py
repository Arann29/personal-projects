import json

import requests
import streamlit as st


API_BASE_URL = "http://api:8000"

st.set_page_config(page_title="data-pipeline-ml", layout="wide")
st.title("Data Pipeline ML Dashboard")
st.caption("Upload CSV, train model, run predictions, and check drift.")

st.header("1) Train model")
train_file = st.file_uploader("Training CSV", type=["csv"], key="train")
if train_file is not None and st.button("Train model", type="primary"):
    files = {"file": (train_file.name, train_file.getvalue(), "text/csv")}
    response = requests.post(f"{API_BASE_URL}/train", files=files, timeout=120)
    if response.ok:
        st.success("Model trained")
        st.json(response.json())
    else:
        st.error(response.text)

st.header("2) Predict")
st.write("Use JSON format with `records`, e.g. from `/sample-payload` endpoint.")
predict_input = st.text_area(
    "Prediction payload",
    value='{"records": [{"feature_1": 8, "feature_2": 4, "feature_3": 2}]}'
)
if st.button("Run prediction"):
    try:
        payload = json.loads(predict_input)
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=60)
        if response.ok:
            st.success("Prediction complete")
            st.json(response.json())
        else:
            st.error(response.text)
    except json.JSONDecodeError:
        st.error("Invalid JSON payload")

st.header("3) Drift check")
drift_file = st.file_uploader("Drift check CSV", type=["csv"], key="drift")
if drift_file is not None and st.button("Run drift check"):
    files = {"file": (drift_file.name, drift_file.getvalue(), "text/csv")}
    response = requests.post(f"{API_BASE_URL}/drift", files=files, timeout=60)
    if response.ok:
        report = response.json()
        if report.get("drift_detected"):
            st.warning("Drift detected")
        else:
            st.success("No drift detected")
        st.json(report)
    else:
        st.error(response.text)

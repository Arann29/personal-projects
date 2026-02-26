import pandas as pd
import requests
import streamlit as st


API_URL = "http://localhost:8005"

st.set_page_config(page_title="Personal Finance Control Center", layout="wide")
st.title("Personal Finance Control Center")

st.subheader("Quick cash entry")
amount = st.number_input("Amount", min_value=0.01, step=0.5)
description = st.text_input("Description", value="Coffee")
merchant = st.text_input("Merchant", value="")

if st.button("Add cash expense"):
    response = requests.post(
        f"{API_URL}/ingest/manual",
        json={"amount": amount, "description": description, "merchant": merchant, "account_name": "Cash"},
        timeout=30,
    )
    if response.ok:
        st.success(response.json())
    else:
        st.error(response.text)

st.divider()
st.subheader("Receipt ingestion (with confidence check)")
receipt_file = st.file_uploader("Upload receipt image", type=["jpg", "jpeg", "png"], key="receipt_upload")

if st.button("Extract receipt data"):
    if receipt_file is None:
        st.warning("Please upload an image first.")
    else:
        files = {"file": (receipt_file.name, receipt_file.getvalue(), receipt_file.type or "image/jpeg")}
        response = requests.post(f"{API_URL}/ingest/receipt", files=files, timeout=60)
        if response.ok:
            payload = response.json()
            st.json(payload)

            if payload.get("requires_review", True):
                st.warning(
                    "This extraction needs review before confirmation. "
                    f"Overall confidence: {payload.get('confidence_score', 0):.2f}"
                )

            low_fields = [
                field_name
                for field_name, score in payload.get("confidence_by_field", {}).items()
                if score < 0.7
            ]
            if low_fields:
                st.warning(f"Low-confidence fields: {', '.join(low_fields)}")
        else:
            st.error(response.text)

st.divider()
st.subheader("Transactions")
if st.button("Refresh transactions"):
    response = requests.get(f"{API_URL}/transactions", timeout=30)
    if response.ok:
        dataframe = pd.DataFrame(response.json())
        if not dataframe.empty:
            st.dataframe(dataframe)
        else:
            st.info("No transactions yet.")
    else:
        st.error(response.text)

st.divider()
st.subheader("Monthly summary")
month = st.text_input("Month (YYYY-MM)", value="2024-12")
if st.button("Load summary"):
    response = requests.get(f"{API_URL}/analytics/monthly/{month}", timeout=30)
    if response.ok:
        payload = response.json()
        st.write(f"Total spent: {payload['total_spent']:.2f}")
        chart_data = pd.DataFrame(payload["by_category"].items(), columns=["category", "amount"]).set_index("category")
        if not chart_data.empty:
            st.bar_chart(chart_data)
    else:
        st.error(response.text)

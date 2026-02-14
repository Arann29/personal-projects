import requests
import streamlit as st


API_BASE_URL = "http://api:8000"

st.set_page_config(page_title="doc-etl dashboard", layout="wide")
st.title("doc-etl Dashboard")
st.caption("Upload documents, run extraction, and review ETL results.")

uploaded_file = st.file_uploader("Upload .txt or .pdf", type=["txt", "pdf"])

if uploaded_file is not None:
    if st.button("Process document", type="primary"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/process", files=files, timeout=60)
        if response.ok:
            st.success("Document processed successfully")
            st.json(response.json())
        else:
            st.error(f"Processing failed: {response.text}")

st.subheader("Recent documents")
response = requests.get(f"{API_BASE_URL}/documents?limit=20", timeout=30)
if response.ok:
    items = response.json().get("items", [])
    if items:
        st.dataframe(items, use_container_width=True)
    else:
        st.info("No documents yet. Upload one to start.")
else:
    st.error("Could not load documents. Is the API running?")

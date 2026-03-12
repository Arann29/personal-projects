# Personal Projects Portfolio

This repository contains my personal data science and machine learning projects.

The goal is to show how I design, build, and deploy practical solutions with a focus on:
- ETL pipelines
- Machine learning workflows
- API development
- Containerization with Docker
- Clear, reproducible project structure

## Projects

### 1) doc-etl
A document processing ETL pipeline.
- Upload text/PDF documents
- Extract structured fields
- Validate and store results in PostgreSQL
- Review outcomes in a Streamlit dashboard

Path: [doc-etl](doc-etl)

### 2) data-pipeline-ml
An end-to-end data + ML pipeline.
- Ingest CSV data
- Clean and transform data
- Train a regression model
- Serve predictions via FastAPI
- Monitor drift against a training baseline

Path: [data-pipeline-ml](data-pipeline-ml)

### 3) investment-etl-reporting
A finance-oriented ETL and reporting pipeline.
- Ingest portfolio price data
- Compute per-ticker return/risk metrics
- Store run history and metrics in PostgreSQL
- Generate markdown performance reports
- Explore results in a Streamlit dashboard

Path: [investment-etl-reporting](investment-etl-reporting)

### 4) sentiment-analysis-nlp
A sentiment and topic analysis NLP pipeline.
- Ingest customer feedback/review text data
- Run transformer-based sentiment classification
- Extract topic clusters with TF-IDF + KMeans
- Store analysis runs and document-level outputs in PostgreSQL
- Visualize sentiment and topic distributions in Streamlit

Path: [sentiment-analysis-nlp](sentiment-analysis-nlp)

## Tech Stack
Python, SQL, FastAPI, Streamlit, scikit-learn, transformers, PostgreSQL, Docker, Docker Compose.

## Why this portfolio
I built these projects to demonstrate production-oriented data work: from ingestion and transformation to model delivery and monitoring.

## Contact
Andres Arostegui Arias
- LinkedIn: https://www.linkedin.com/in/andresarostegui95/
- Email: andres.arostegui95@gmail.com

_Last remote push access test by OpenClaw on 2026-03-12._

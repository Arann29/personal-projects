from collections import Counter

from fastapi import FastAPI, File, HTTPException, UploadFile

from src.etl.extract import extract_csv
from src.etl.load import (
    create_analysis_run,
    fetch_documents,
    fetch_results,
    insert_documents,
    latest_run_id,
    save_analysis_results,
)
from src.etl.transform import transform_dataframe
from src.models.schemas import AnalyzeRequest, AnalyzeResponse, IngestResponse, ResultsResponse, SummaryResponse
from src.nlp.sentiment import score_texts
from src.nlp.summarize import generate_summary
from src.nlp.topics import build_topics


app = FastAPI(title="sentiment-analysis-nlp API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        payload = await file.read()
        frame = extract_csv(payload)
        transformed, dropped_rows = transform_dataframe(frame)
        rows = transformed.to_dict(orient="records")
        loaded_count = insert_documents(file.filename or "uploaded.csv", rows)

        return IngestResponse(
            rows_loaded=loaded_count,
            rows_dropped=int(dropped_rows),
            columns=list(transformed.columns),
        )
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        documents = fetch_documents()
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found. Run /ingest first.")

        texts = [row["cleaned_text"] for row in documents]
        sentiment_rows = score_texts(texts)
        topic_assignments, topic_keywords, topics_used = build_topics(texts, request.topic_count)

        run_id = create_analysis_run(
            model_name="distilbert-base-uncased-finetuned-sst-2-english",
            topic_count=topics_used,
        )

        records_to_save: list[dict] = []
        sentiment_distribution: Counter = Counter()

        for document, sentiment_row, topic_id in zip(documents, sentiment_rows, topic_assignments):
            sentiment_distribution[sentiment_row["sentiment_label"]] += 1
            records_to_save.append(
                {
                    "document_id": document["id"],
                    "sentiment_label": sentiment_row["sentiment_label"],
                    "sentiment_score": sentiment_row["sentiment_score"],
                    "topic_id": int(topic_id),
                    "topic_keywords": topic_keywords[int(topic_id)],
                }
            )

        save_analysis_results(run_id, records_to_save)

        return AnalyzeResponse(
            run_id=run_id,
            documents_analyzed=len(documents),
            topics_used=topics_used,
            sentiment_distribution=dict(sentiment_distribution),
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/results", response_model=ResultsResponse)
def results(run_id: int | None = None):
    target_run_id = run_id or latest_run_id()
    if not target_run_id:
        raise HTTPException(status_code=404, detail="No analysis run found")

    rows = fetch_results(target_run_id)
    records = [
        {
            "document_id": row["document_id"],
            "raw_text_preview": row["raw_text"][:160],
            "sentiment_label": row["sentiment_label"],
            "sentiment_score": row["sentiment_score"],
            "topic_id": row["topic_id"],
            "topic_keywords": row["topic_keywords"],
        }
        for row in rows
    ]

    return ResultsResponse(run_id=target_run_id, records=records)


@app.get("/summary", response_model=SummaryResponse)
def summary(run_id: int | None = None):
    target_run_id = run_id or latest_run_id()
    if not target_run_id:
        raise HTTPException(status_code=404, detail="No analysis run found")

    rows = fetch_results(target_run_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No results for this run")

    sentiments = [row["sentiment_label"] for row in rows]
    topics = [row["topic_keywords"] for row in rows]
    sample_texts = [row["raw_text"] for row in rows]
    summary_text = generate_summary(sentiments, topics, sample_texts)

    return SummaryResponse(run_id=target_run_id, summary_text=summary_text)

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    rows_loaded: int
    rows_dropped: int
    columns: list[str]


class AnalyzeRequest(BaseModel):
    topic_count: int = Field(default=4, ge=2, le=10)


class AnalyzeResponse(BaseModel):
    run_id: int
    documents_analyzed: int
    topics_used: int
    sentiment_distribution: dict[str, int]


class ResultRecord(BaseModel):
    document_id: int
    raw_text_preview: str
    sentiment_label: str
    sentiment_score: float
    topic_id: int
    topic_keywords: str


class ResultsResponse(BaseModel):
    run_id: int
    records: list[ResultRecord]


class SummaryResponse(BaseModel):
    run_id: int
    summary_text: str

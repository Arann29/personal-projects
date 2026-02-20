CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    source_filename TEXT NOT NULL,
    review_date DATE NULL,
    rating INTEGER NULL,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    topic_count INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    sentiment_label TEXT NOT NULL,
    sentiment_score DOUBLE PRECISION NOT NULL,
    topic_id INTEGER NOT NULL,
    topic_keywords TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

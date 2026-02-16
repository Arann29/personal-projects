CREATE TABLE IF NOT EXISTS ingestion_runs (
    id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    rows_loaded INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investment_metrics (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES ingestion_runs(id) ON DELETE CASCADE,
    ticker TEXT NOT NULL,
    avg_daily_return DOUBLE PRECISION,
    volatility DOUBLE PRECISION,
    total_return DOUBLE PRECISION,
    max_drawdown DOUBLE PRECISION,
    annualized_return DOUBLE PRECISION,
    annualized_volatility DOUBLE PRECISION,
    sharpe_ratio DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES ingestion_runs(id) ON DELETE CASCADE,
    report_markdown TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

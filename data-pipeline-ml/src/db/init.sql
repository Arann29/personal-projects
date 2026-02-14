CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS training_baseline (
    id SERIAL PRIMARY KEY,
    feature_name TEXT NOT NULL,
    mean_value DOUBLE PRECISION,
    std_value DOUBLE PRECISION,
    missing_rate DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions_log (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    prediction DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS pipeline_errors (
    id SERIAL PRIMARY KEY,
    stage TEXT NOT NULL,
    error_message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

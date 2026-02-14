CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS extracted_records (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    vendor_name TEXT,
    invoice_number TEXT,
    invoice_date DATE,
    due_date DATE,
    currency TEXT,
    total_amount NUMERIC(14,2),
    tax_amount NUMERIC(14,2),
    category TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_errors (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    stage TEXT NOT NULL,
    error_message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

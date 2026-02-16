from fastapi import FastAPI, File, HTTPException, UploadFile
from sqlalchemy import text

from src.db.database import engine
from src.services.etl import extract_csv, transform_data
from src.services.metrics import calculate_metrics
from src.services.reporting import build_markdown_report

app = FastAPI(title="investment-etl-reporting API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    try:
        payload = await file.read()
        raw_frame = extract_csv(payload)
        transformed = transform_data(raw_frame)
        metrics = calculate_metrics(transformed)

        with engine.begin() as connection:
            run_result = connection.execute(
                text("INSERT INTO ingestion_runs (source_name, rows_loaded) VALUES (:source_name, :rows_loaded) RETURNING id"),
                {
                    "source_name": file.filename or "uploaded.csv",
                    "rows_loaded": int(len(transformed)),
                },
            )
            run_id = int(run_result.scalar_one())

            for _, row in metrics.iterrows():
                connection.execute(
                    text(
                        """
                        INSERT INTO investment_metrics (
                            run_id, ticker, avg_daily_return, volatility, total_return,
                            max_drawdown, annualized_return, annualized_volatility, sharpe_ratio
                        ) VALUES (
                            :run_id, :ticker, :avg_daily_return, :volatility, :total_return,
                            :max_drawdown, :annualized_return, :annualized_volatility, :sharpe_ratio
                        )
                        """
                    ),
                    {
                        "run_id": run_id,
                        "ticker": row["ticker"],
                        "avg_daily_return": float(row["avg_daily_return"]),
                        "volatility": float(row["volatility"]),
                        "total_return": float(row["total_return"]),
                        "max_drawdown": float(row["max_drawdown"]),
                        "annualized_return": float(row["annualized_return"]),
                        "annualized_volatility": float(row["annualized_volatility"]),
                        "sharpe_ratio": float(row["sharpe_ratio"]),
                    },
                )

        return {
            "run_id": run_id,
            "rows_loaded": int(len(transformed)),
            "tickers": sorted(metrics["ticker"].tolist()),
        }
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/metrics/summary")
def metrics_summary(run_id: int | None = None) -> dict:
    try:
        with engine.begin() as connection:
            if run_id is None:
                latest = connection.execute(text("SELECT id FROM ingestion_runs ORDER BY id DESC LIMIT 1")).scalar()
                if latest is None:
                    raise ValueError("No ingestion runs found")
                run_id = int(latest)

            rows = connection.execute(
                text(
                    """
                    SELECT ticker, avg_daily_return, volatility, total_return,
                           max_drawdown, annualized_return, annualized_volatility, sharpe_ratio
                    FROM investment_metrics
                    WHERE run_id = :run_id
                    ORDER BY annualized_return DESC
                    """
                ),
                {"run_id": run_id},
            ).mappings().all()

            if not rows:
                raise ValueError(f"No metrics found for run_id={run_id}")

            response_rows = []
            for row in rows:
                response_rows.append({key: float(value) if isinstance(value, (int, float)) and key != "ticker" else value for key, value in row.items()})

            best = rows[0]
            highest_vol = sorted(rows, key=lambda item: item["volatility"], reverse=True)[0]

            return {
                "run_id": run_id,
                "ticker_count": len(rows),
                "best_annualized_return": {
                    "ticker": best["ticker"],
                    "annualized_return": float(best["annualized_return"]),
                },
                "highest_volatility": {
                    "ticker": highest_vol["ticker"],
                    "volatility": float(highest_vol["volatility"]),
                },
                "metrics": response_rows,
            }
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/report")
def generate_report(run_id: int | None = None) -> dict:
    try:
        with engine.begin() as connection:
            if run_id is None:
                latest = connection.execute(text("SELECT id FROM ingestion_runs ORDER BY id DESC LIMIT 1")).scalar()
                if latest is None:
                    raise ValueError("No ingestion runs found")
                run_id = int(latest)

            rows_loaded = connection.execute(
                text("SELECT rows_loaded FROM ingestion_runs WHERE id = :run_id"),
                {"run_id": run_id},
            ).scalar()
            if rows_loaded is None:
                raise ValueError(f"Run {run_id} not found")

            rows = connection.execute(
                text(
                    """
                    SELECT ticker, avg_daily_return, volatility, total_return,
                           max_drawdown, annualized_return, annualized_volatility, sharpe_ratio
                    FROM investment_metrics
                    WHERE run_id = :run_id
                    ORDER BY annualized_return DESC
                    """
                ),
                {"run_id": run_id},
            ).mappings().all()
            if not rows:
                raise ValueError(f"No metrics found for run_id={run_id}")

            import pandas as pd

            metrics = pd.DataFrame(rows)
            report_markdown = build_markdown_report(metrics, int(rows_loaded))

            report_id = connection.execute(
                text(
                    "INSERT INTO generated_reports (run_id, report_markdown) VALUES (:run_id, :report_markdown) RETURNING id"
                ),
                {"run_id": run_id, "report_markdown": report_markdown},
            ).scalar_one()

            return {
                "report_id": int(report_id),
                "run_id": run_id,
                "report_markdown": report_markdown,
            }
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/report/latest")
def latest_report() -> dict:
    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT id, run_id, report_markdown, created_at
                    FROM generated_reports
                    ORDER BY id DESC
                    LIMIT 1
                    """
                )
            ).mappings().first()
            if row is None:
                raise ValueError("No reports generated yet")

            return {
                "report_id": int(row["id"]),
                "run_id": int(row["run_id"]),
                "created_at": str(row["created_at"]),
                "report_markdown": row["report_markdown"],
            }
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

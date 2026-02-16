from datetime import datetime

import pandas as pd


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _fmt_num(value: float) -> str:
    return f"{value:.4f}"


def build_markdown_report(metrics: pd.DataFrame, rows_loaded: int) -> str:
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    best_ticker = metrics.sort_values("annualized_return", ascending=False).iloc[0]
    riskiest_ticker = metrics.sort_values("volatility", ascending=False).iloc[0]

    lines = [
        "# Investment Performance Report",
        "",
        f"- Generated at: {generated_at}",
        f"- Rows processed: {rows_loaded}",
        f"- Tickers covered: {metrics['ticker'].nunique()}",
        "",
        "## Highlights",
        f"- Best annualized return: {best_ticker['ticker']} ({_fmt_pct(best_ticker['annualized_return'])})",
        f"- Highest volatility: {riskiest_ticker['ticker']} ({_fmt_pct(riskiest_ticker['volatility'])})",
        "",
        "## Ticker Metrics",
        "",
        "| Ticker | Total Return | Annualized Return | Annualized Volatility | Sharpe | Max Drawdown |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    sorted_metrics = metrics.sort_values("annualized_return", ascending=False)
    for _, row in sorted_metrics.iterrows():
        lines.append(
            "| "
            + f"{row['ticker']} | {_fmt_pct(row['total_return'])} | {_fmt_pct(row['annualized_return'])} | "
            + f"{_fmt_pct(row['annualized_volatility'])} | {_fmt_num(row['sharpe_ratio'])} | {_fmt_pct(row['max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "- Daily returns are computed from closing prices by ticker.",
            "- Sharpe ratio uses a 1% annual risk-free rate.",
            "- This is a demo pipeline and not financial advice.",
        ]
    )

    return "\n".join(lines)

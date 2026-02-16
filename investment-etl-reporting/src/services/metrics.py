import numpy as np
import pandas as pd

TRADING_DAYS = 252
RISK_FREE_RATE = 0.01


def _max_drawdown(returns: pd.Series) -> float:
    cumulative = (1 + returns.fillna(0)).cumprod()
    running_peak = cumulative.cummax()
    drawdown = (cumulative - running_peak) / running_peak
    return float(drawdown.min())


def calculate_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for ticker, group in frame.groupby("ticker"):
        prices = group.sort_values("date").copy()
        prices["daily_return"] = prices["close"].pct_change()
        daily_returns = prices["daily_return"].dropna()

        if daily_returns.empty:
            avg_daily = 0.0
            volatility = 0.0
            total_return = 0.0
            max_drawdown = 0.0
            annualized_return = 0.0
            annualized_volatility = 0.0
            sharpe = 0.0
        else:
            avg_daily = float(daily_returns.mean())
            volatility = float(daily_returns.std(ddof=1)) if len(daily_returns) > 1 else 0.0
            total_return = float((prices["close"].iloc[-1] / prices["close"].iloc[0]) - 1)
            max_drawdown = _max_drawdown(daily_returns)
            annualized_return = float((1 + avg_daily) ** TRADING_DAYS - 1)
            annualized_volatility = float(volatility * np.sqrt(TRADING_DAYS))
            if annualized_volatility > 0:
                sharpe = float((annualized_return - RISK_FREE_RATE) / annualized_volatility)
            else:
                sharpe = 0.0

        rows.append(
            {
                "ticker": ticker,
                "avg_daily_return": avg_daily,
                "volatility": volatility,
                "total_return": total_return,
                "max_drawdown": max_drawdown,
                "annualized_return": annualized_return,
                "annualized_volatility": annualized_volatility,
                "sharpe_ratio": sharpe,
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("Unable to calculate metrics")
    return result

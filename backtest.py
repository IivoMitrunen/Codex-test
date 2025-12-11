"""
Backtesting utilities for BTC range-sweep strategy.

Two entry points are provided:
1) Download OHLCV data from Binance using ccxt and save it as CSV.
2) Analyze an existing CSV to generate sweep-based trade signals.

The strategy rules are:
- Trade long only when price is above the 50 EMA and 50 EMA is above the 200 EMA.
- Trade short only when price is below the 50 EMA and 50 EMA is below the 200 EMA.
- Identify 1H swing highs/lows with a three-candle pivot on each side.
- A range forms once both a swing high and swing low exist with at least three bars between them.
- For longs: wait for a sweep of the range low followed by a close above the range high (structure break).
- For shorts: wait for a sweep of the range high followed by a close below the range low (structure break).
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import ccxt
import numpy as np
import pandas as pd


@dataclass
class Signal:
    index: pd.Timestamp
    direction: str
    reason: str
    close: float
    range_high: float
    range_low: float


@dataclass
class RangeState:
    last_swing_high: Optional[int]
    last_swing_low: Optional[int]
    range_high: Optional[float]
    range_low: Optional[float]
    sweep_pending: Optional[str]


PIVOT_WIDTH = 3


def download_ohlcv_csv(symbol: str, timeframe: str, limit: int, output: Path) -> None:
    exchange = ccxt.binance()
    candles = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(candles, columns=columns)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Saved {len(df)} candles to {output}")


def calculate_emas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
    return df


def find_pivots(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    highs = df["high"].values
    lows = df["low"].values

    pivot_highs = np.full(len(df), False)
    pivot_lows = np.full(len(df), False)

    for i in range(PIVOT_WIDTH, len(df) - PIVOT_WIDTH):
        window_highs = highs[i - PIVOT_WIDTH : i + PIVOT_WIDTH + 1]
        window_lows = lows[i - PIVOT_WIDTH : i + PIVOT_WIDTH + 1]
        pivot_highs[i] = highs[i] == window_highs.max()
        pivot_lows[i] = lows[i] == window_lows.min()

    df["pivot_high"] = pivot_highs
    df["pivot_low"] = pivot_lows
    return df


def update_range_state(state: RangeState, idx: int, row: pd.Series) -> RangeState:
    last_high = state.last_swing_high
    last_low = state.last_swing_low

    if row["pivot_high"]:
        last_high = idx
    if row["pivot_low"]:
        last_low = idx

    range_high = state.range_high
    range_low = state.range_low

    if last_high is not None and last_low is not None:
        if abs(last_high - last_low) >= PIVOT_WIDTH:
            range_high = row["high"] if row["pivot_high"] else state.range_high or row["high"]
            range_low = row["low"] if row["pivot_low"] else state.range_low or row["low"]

    sweep_pending = state.sweep_pending
    return RangeState(last_high, last_low, range_high, range_low, sweep_pending)


def analyze_signals(df: pd.DataFrame) -> List[Signal]:
    signals: List[Signal] = []
    state = RangeState(None, None, None, None, None)

    for idx, row in df.iterrows():
        state = update_range_state(state, idx, row)
        if state.range_high is None or state.range_low is None:
            continue

        bullish_bias = row["close"] > row["ema50"] > row["ema200"]
        bearish_bias = row["close"] < row["ema50"] < row["ema200"]

        if bullish_bias:
            if row["low"] < state.range_low:
                state.sweep_pending = "long"
            if state.sweep_pending == "long" and row["close"] > state.range_high:
                signals.append(
                    Signal(
                        index=row["timestamp"],
                        direction="long",
                        reason="Range low swept, structure broke above range high",
                        close=row["close"],
                        range_high=state.range_high,
                        range_low=state.range_low,
                    )
                )
                state.sweep_pending = None

        if bearish_bias:
            if row["high"] > state.range_high:
                state.sweep_pending = "short"
            if state.sweep_pending == "short" and row["close"] < state.range_low:
                signals.append(
                    Signal(
                        index=row["timestamp"],
                        direction="short",
                        reason="Range high swept, structure broke below range low",
                        close=row["close"],
                        range_high=state.range_high,
                        range_low=state.range_low,
                    )
                )
                state.sweep_pending = None

    return signals


def load_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def run_signal_report(csv_path: Path) -> None:
    df = load_csv(csv_path)
    df = calculate_emas(df)
    df = find_pivots(df)
    signals = analyze_signals(df)

    if not signals:
        print("No signals detected with current parameters.")
        return

    print("timestamp,direction,close,range_high,range_low,reason")
    for signal in signals:
        print(
            f"{signal.index.isoformat()},{signal.direction},{signal.close:.2f},{signal.range_high:.2f},{signal.range_low:.2f},{signal.reason}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BTC range sweep strategy tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dl = subparsers.add_parser("download", help="Download OHLCV data as CSV")
    dl.add_argument("--symbol", default="BTC/USDT", help="Trading pair, e.g., BTC/USDT")
    dl.add_argument("--timeframe", default="1h", help="Exchange timeframe (default: 1h)")
    dl.add_argument("--limit", type=int, default=1500, help="Number of candles to fetch")
    dl.add_argument("--output", type=Path, default=Path("data/btc_1h.csv"), help="CSV file path")

    signals = subparsers.add_parser("signals", help="Generate trading signals from a CSV")
    signals.add_argument("csv", type=Path, help="Path to OHLCV CSV file")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "download":
        download_ohlcv_csv(args.symbol, args.timeframe, args.limit, args.output)
    elif args.command == "signals":
        run_signal_report(args.csv)


if __name__ == "__main__":
    main()

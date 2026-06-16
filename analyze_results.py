from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

CSV_PATH = Path("results.csv")
CHUNK_SIZE = 500_000
P99_QUANTILE = 0.99


class LatencyStats(NamedTuple):
    total_messages: int
    rps: float
    mean_ms: float
    min_ms: float
    max_ms: float
    p99_ms: float
    elapsed_s: float


def _validate_file(path: Path) -> None:
    if not path.exists():
        print(f"[ERROR] File not found: {path.resolve()}", file=sys.stderr)
        sys.exit(1)
    if path.stat().st_size == 0:
        print(f"[ERROR] File is empty: {path.resolve()}", file=sys.stderr)
        sys.exit(1)


def _stream_metrics(path: Path) -> tuple[int, float, float, float, np.ndarray, pd.Timestamp, pd.Timestamp]:
    count = 0
    lat_sum = 0.0
    lat_min = np.inf
    lat_max = -np.inf
    lat_chunks: list[np.ndarray] = []
    ts_min: pd.Timestamp | None = None
    ts_max: pd.Timestamp | None = None

    reader = pd.read_csv(
        path,
        usecols=["timestamp", "latency_ms"],
        dtype={"latency_ms": "float32"},
        parse_dates=["timestamp"],
        chunksize=CHUNK_SIZE,
        engine="c",
    )

    for chunk in reader:
        lat = chunk["latency_ms"].to_numpy(dtype="float64")
        ts = chunk["timestamp"]

        count += len(lat)
        lat_sum += float(lat.sum())
        lat_min = min(lat_min, float(lat.min()))
        lat_max = max(lat_max, float(lat.max()))
        lat_chunks.append(lat)

        chunk_ts_min = ts.min()
        chunk_ts_max = ts.max()

        if ts_min is None or chunk_ts_min < ts_min:
            ts_min = chunk_ts_min
        if ts_max is None or chunk_ts_max > ts_max:
            ts_max = chunk_ts_max

    return count, lat_sum, lat_min, lat_max, np.concatenate(lat_chunks), ts_min, ts_max


def compute_stats(path: Path) -> LatencyStats:
    t0 = time.monotonic()
    count, lat_sum, lat_min, lat_max, all_latencies, ts_min, ts_max = _stream_metrics(path)
    elapsed = time.monotonic() - t0

    if count == 0:
        print("[ERROR] CSV contains no data rows.", file=sys.stderr)
        sys.exit(1)

    mean_ms = lat_sum / count
    p99_ms = float(np.percentile(all_latencies, P99_QUANTILE * 100))

    duration_s = (ts_max - ts_min).total_seconds() if ts_min != ts_max else 1.0
    rps = count / duration_s if duration_s > 0 else float("inf")

    return LatencyStats(
        total_messages=count,
        rps=rps,
        mean_ms=mean_ms,
        min_ms=lat_min,
        max_ms=lat_max,
        p99_ms=p99_ms,
        elapsed_s=elapsed,
    )


def print_report(stats: LatencyStats, path: Path) -> None:
    file_size_mb = path.stat().st_size / 1024 ** 2
    separator = "=" * 56

    print(f"\n{separator}")
    print(f"  Performance Analysis Report")
    print(f"  Source : {path.resolve()}")
    print(f"  Size   : {file_size_mb:.2f} MB  |  Processed in {stats.elapsed_s:.2f}s")
    print(separator)
    print(f"  {'Metric':<30} {'Value':>20}")
    print(f"  {'-'*30} {'-'*20}")
    print(f"  {'Total Messages':<30} {stats.total_messages:>20,}")
    print(f"  {'Requests Per Second (RPS)':<30} {stats.rps:>19.2f}")
    print(f"  {'Mean Latency':<30} {stats.mean_ms:>18.3f} ms")
    print(f"  {'Min Latency':<30} {stats.min_ms:>18.3f} ms")
    print(f"  {'Max Latency':<30} {stats.max_ms:>18.3f} ms")
    print(f"  {'p99 Latency':<30} {stats.p99_ms:>18.3f} ms")
    print(f"{separator}\n")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PATH
    _validate_file(path)
    print(f"Loading '{path}' in chunks of {CHUNK_SIZE:,} rows...")
    stats = compute_stats(path)
    print_report(stats, path)


if __name__ == "__main__":
    main()
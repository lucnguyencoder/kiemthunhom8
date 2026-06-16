from __future__ import annotations

import asyncio
import csv
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev
from typing import NamedTuple

import websockets
from websockets.exceptions import ConnectionClosed

URI = "ws://localhost:8000/live-match"
NUM_CLIENTS = 5_000
OUTPUT_FILE = Path("results.csv")
CONNECT_BATCH = 200
CONNECT_DELAY = 0.05
MAX_MESSAGES = 50


class Record(NamedTuple):
    connection_id: int
    timestamp: str
    latency_ms: float


@dataclass
class RunStats:
    records: list[Record] = field(default_factory=list)
    errors: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def add(self, record: Record) -> None:
        async with self.lock:
            self.records.append(record)

    async def inc_error(self) -> None:
        async with self.lock:
            self.errors += 1


def _parse_server_ts(raw: str) -> float:
    dt = datetime.fromisoformat(raw)
    return dt.timestamp() * 1000.0


async def run_client(
    conn_id: int,
    stats: RunStats,
    semaphore: asyncio.Semaphore,
) -> None:
    async with semaphore:
        try:
            async with websockets.connect(
                URI,
                open_timeout=15,
                close_timeout=5,
                max_size=2**20,
                ping_interval=None,
            ) as ws:
                count = 0
                async for raw in ws:
                    recv_ms = time.time() * 1000.0
                    try:
                        payload = json.loads(raw)
                        server_ts_ms = _parse_server_ts(payload["timestamp"])
                        latency = recv_ms - server_ts_ms
                        ts_label = payload["timestamp"]
                    except (KeyError, ValueError, json.JSONDecodeError):
                        await stats.inc_error()
                        continue

                    await stats.add(Record(conn_id, ts_label, round(latency, 3)))
                    count += 1

                    if count >= MAX_MESSAGES or payload.get("match", {}).get("status") == "FINISHED":
                        break
        except (ConnectionClosed, OSError, TimeoutError, websockets.exceptions.WebSocketException):
            await stats.inc_error()


def _write_csv(records: list[Record]) -> None:
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["connection_id", "timestamp", "latency_ms"])
        for r in records:
            writer.writerow([r.connection_id, r.timestamp, r.latency_ms])


def _print_summary(stats: RunStats, elapsed: float) -> None:
    latencies = [r.latency_ms for r in stats.records]
    total = len(latencies)
    print("\n" + "=" * 60)
    print(f"  Performance Test Summary")
    print("=" * 60)
    print(f"  Clients targeted      : {NUM_CLIENTS:,}")
    print(f"  Total messages        : {total:,}")
    print(f"  Errors / failures     : {stats.errors:,}")
    print(f"  Elapsed time          : {elapsed:.2f}s")
    if total:
        print(f"  Latency min           : {min(latencies):.3f} ms")
        print(f"  Latency max           : {max(latencies):.3f} ms")
        print(f"  Latency mean          : {mean(latencies):.3f} ms")
        print(f"  Latency median        : {median(latencies):.3f} ms")
        if total > 1:
            print(f"  Latency stdev         : {stdev(latencies):.3f} ms")
        p95 = sorted(latencies)[int(total * 0.95)]
        p99 = sorted(latencies)[int(total * 0.99)]
        print(f"  Latency p95           : {p95:.3f} ms")
        print(f"  Latency p99           : {p99:.3f} ms")
    print(f"  Results saved to      : {OUTPUT_FILE.resolve()}")
    print("=" * 60 + "\n")


async def main() -> None:
    print(f"Starting perf test: {NUM_CLIENTS:,} concurrent WebSocket clients → {URI}")
    stats = RunStats()
    semaphore = asyncio.Semaphore(NUM_CLIENTS)

    tasks: list[asyncio.Task] = []
    t_start = time.monotonic()

    for batch_start in range(0, NUM_CLIENTS, CONNECT_BATCH):
        batch_end = min(batch_start + CONNECT_BATCH, NUM_CLIENTS)
        for conn_id in range(batch_start, batch_end):
            task = asyncio.create_task(run_client(conn_id, stats, semaphore))
            tasks.append(task)
        if batch_end < NUM_CLIENTS:
            await asyncio.sleep(CONNECT_DELAY)
        if batch_start % 1000 == 0 and batch_start > 0:
            print(f"  Launched {batch_start:,} / {NUM_CLIENTS:,} clients...", flush=True)

    print(f"  All {NUM_CLIENTS:,} tasks dispatched. Waiting for completion...")
    await asyncio.gather(*tasks, return_exceptions=True)

    elapsed = time.monotonic() - t_start
    _write_csv(stats.records)
    _print_summary(stats, elapsed)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
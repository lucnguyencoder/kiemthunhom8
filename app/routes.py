import asyncio
import json
import time
from statistics import mean, median, stdev

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import websockets
from websockets.exceptions import ConnectionClosed

from app.connection import manager
from app.generator import create_initial_state, generate_tick, create_state_from_match_data, PREMIER_LEAGUE_TEAMS
from app.football_api import client as football_data_client

BROADCAST_INTERVAL = 0.2

router = APIRouter()


@router.get("/teams")
async def get_teams():
    """Return list of Premier League teams"""
    return {"teams": list(PREMIER_LEAGUE_TEAMS.keys())}


@router.get("/matches")
async def get_matches():
    """Get live/recent matches from Football-Data.org"""
    matches = await football_data_client.get_live_matches()
    
    result = []
    for match in matches:
        result.append({
            "id": match.get("id"),
            "homeTeam": match.get("homeTeam", {}).get("name", ""),
            "awayTeam": match.get("awayTeam", {}).get("name", ""),
            "status": match.get("status"),
            "utcDate": match.get("utcDate"),
            "score": match.get("score", {}),
        })
    
    return {"matches": result}


@router.websocket("/live-match")
async def live_match(
    websocket: WebSocket,
    home_team: str = Query("Arsenal"),
    away_team: str = Query("Chelsea"),
    match_id: int = Query(None),
):
    await manager.connect(websocket)
    
    # If match_id provided, try to fetch real data
    if match_id:
        match_data = await football_data_client.get_match_detail(match_id)
        if match_data:
            state = create_state_from_match_data(match_data)
        else:
            state = create_initial_state(home_team, away_team)
    else:
        state = create_initial_state(home_team, away_team)
    
    try:
        while True:
            payload = generate_tick(state, home_team, away_team)
            await manager.send(websocket, payload.model_dump_json())
            if state.status == "FINISHED":
                break
            await asyncio.sleep(BROADCAST_INTERVAL)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


@router.post("/perf-test")
async def perf_test(
    home_team: str = Query("Arsenal"),
    away_team: str = Query("Chelsea"),
    num_clients: int = Query(1000),
):
    """Run performance test and return statistics"""
    import statistics
    
    URI = "ws://localhost:8000/live-match"
    CONNECT_BATCH = 200
    CONNECT_DELAY = 0.05
    MAX_MESSAGES = 50
    
    class Record:
        def __init__(self, connection_id, latency_ms):
            self.connection_id = connection_id
            self.latency_ms = latency_ms
    
    records = []
    errors = 0
    lock = asyncio.Lock()
    
    async def run_client(conn_id):
        nonlocal errors
        try:
            ws_url = f"{URI}?home_team={home_team}&away_team={away_team}"
            async with websockets.connect(
                ws_url,
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
                        timestamp = payload["timestamp"]
                        # Parse ISO timestamp
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp)
                        server_ts_ms = dt.timestamp() * 1000.0
                        latency = recv_ms - server_ts_ms
                    except (KeyError, ValueError):
                        async with lock:
                            errors += 1
                        continue
                    
                    async with lock:
                        records.append(Record(conn_id, round(latency, 3)))
                    
                    count += 1
                    if count >= MAX_MESSAGES or payload.get("match", {}).get("status") == "FINISHED":
                        break
        except (ConnectionClosed, OSError, TimeoutError):
            async with lock:
                errors += 1
    
    # Run test
    semaphore = asyncio.Semaphore(num_clients)
    tasks = []
    t_start = time.monotonic()
    
    for batch_start in range(0, num_clients, CONNECT_BATCH):
        batch_end = min(batch_start + CONNECT_BATCH, num_clients)
        for conn_id in range(batch_start, batch_end):
            async def run_with_semaphore():
                async with semaphore:
                    await run_client(conn_id)
            
            task = asyncio.create_task(run_with_semaphore())
            tasks.append(task)
        
        if batch_end < num_clients:
            await asyncio.sleep(CONNECT_DELAY)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.monotonic() - t_start
    
    # Calculate statistics
    if records:
        latencies = [r.latency_ms for r in records]
        total = len(latencies)
        result = {
            "home_team": home_team,
            "away_team": away_team,
            "test_duration_s": round(elapsed, 2),
            "clients_targeted": num_clients,
            "total_messages": total,
            "errors": errors,
            "latency": {
                "min_ms": round(min(latencies), 3),
                "max_ms": round(max(latencies), 3),
                "mean_ms": round(mean(latencies), 3),
                "median_ms": round(median(latencies), 3),
                "stdev_ms": round(stdev(latencies), 3) if total > 1 else 0,
                "p95_ms": round(sorted(latencies)[int(total * 0.95)], 3),
                "p99_ms": round(sorted(latencies)[int(total * 0.99)], 3),
            }
        }
    else:
        result = {
            "home_team": home_team,
            "away_team": away_team,
            "test_duration_s": round(elapsed, 2),
            "clients_targeted": num_clients,
            "total_messages": 0,
            "errors": errors,
            "latency": {}
        }
    
    return result
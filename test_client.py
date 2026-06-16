import asyncio
import json
import websockets


async def watch_match() -> None:
    uri = "ws://localhost:8000/live-match"
    async with websockets.connect(uri) as ws:
        while True:
            raw = await ws.recv()
            data = json.loads(raw)
            match = data["match"]
            home = match["home"]
            away = match["away"]
            event = match.get("latest_event", {})
            print(
                f"[{match['minute']}'] "
                f"{home['name']} {home['score']} - {away['score']} {away['name']} | "
                f"Possession {home['possession']}%/{away['possession']}% | "
                f"{event.get('event_type', '')} — {event.get('description', '')}"
            )
            if match["status"] == "FINISHED":
                print("Match finished.")
                break


if __name__ == "__main__":
    asyncio.run(watch_match())
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Football Live Match Mock Server",
        version="1.0.0",
        description="Streams real-time football match events via WebSocket.",
    )
    app.include_router(router)
    
    # Serve static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Serve index.html as root
    @app.get("/")
    async def root():
        return FileResponse(static_dir / "index.html")
    
    return app


app = create_app()
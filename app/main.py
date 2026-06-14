"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from pathlib import Path

import qrcode
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rich.console import Console
from rich.panel import Panel

from app.api.router import router
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base

# Eager-import all model modules so SQLAlchemy can resolve string relationship references
import app.models.user  # noqa: F401
import app.models.expression  # noqa: F401
import app.models.memory  # noqa: F401
import app.models.session  # noqa: F401
import app.models.mistake  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: create tables on startup if needed."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow all origins for local network use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static images directory
images_dir = settings.image_dir
images_dir.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")

# Include API routes
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


def show_qr_and_url():
    """Display QR code and LAN URL on server start."""
    import socket

    console = Console()

    # Get LAN IP
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"

    url = f"http://{local_ip}:{settings.port}"

    # Generate QR code
    qr = qrcode.QRCode(border=2, box_size=8)
    qr.add_data(url)
    qr.make(fit=True)

    console.print()
    console.print(Panel(
        f"[bold cyan]learnEnglish est prêt ![/bold cyan]\n\n"
        f"[yellow]URL locale :[/yellow] {url}\n"
        f"[yellow]URL serveur :[/yellow] http://0.0.0.0:{settings.port}\n\n"
        f"Scanne le QR code sur ton téléphone (même LAN) :",
        title="🚀 Apprentissage des Phrasal Verbs",
        border_style="green",
    ))

    # Render QR as ASCII art
    import io
    buf = io.StringIO()
    qr.print_ascii(out=buf)
    console.print(buf.getvalue())

    # Save URL to file
    url_file = settings.project_root / "url.txt"
    url_file.write_text(url)
    console.print(f"[dim]URL sauvegardée dans {url_file}[/dim]")


def main():
    import uvicorn
    show_qr_and_url()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    main()

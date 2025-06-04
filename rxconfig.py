import reflex as rx
import os

# Production/Development environment detection
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
PORT = int(os.getenv("PORT", 3000))

config = rx.Config(
    app_name="mi_app_estudio",
    ui_name="Smart Student",
    title="Smart Student | Aprende, Crea y Destaca",
    env=ENV,
    api_url=f"http://localhost:{PORT}" if ENV == "development" else None,
    deploy_url=None if ENV == "development" else "",
)
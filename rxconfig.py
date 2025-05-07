import reflex as rx
import os

# Get GitHub Codespace URL from environment if available
codespace_name = os.environ.get("CODESPACE_NAME", "")
codespace_domain = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")

# Construct the base URLs for GitHub Codespaces
frontend_port = 3000
backend_port = 8000

# Use fixed ports for stability in Codespaces
config = rx.Config(
    app_name="mi_app_estudio",
    ui_name="Smart Student",
    title="Smart Student | Aprende, Crea y Destaca",
    
    # Fixed port configuration
    frontend_port=frontend_port,
    backend_port=backend_port,
    
    # Configure API URL specifically for GitHub Codespaces
    api_url=f"https://{codespace_name}-{backend_port}.{codespace_domain}" if codespace_name else None,
    deploy_url=f"https://{codespace_name}-{frontend_port}.{codespace_domain}" if codespace_name else "http://localhost:3000",
    
    # Ensure the backend host is accessible
    backend_host="0.0.0.0",
    
    # Disable version checking for Next.js to avoid connection errors
    next_dev_indicators=False,
)
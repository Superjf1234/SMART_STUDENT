# Dockerfile optimizado para Railway - aplicación SMART_STUDENT Reflex
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js LTS (más estable para Railway)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Instalar bun con configuración optimizada
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"
ENV BUN_INSTALL="/root/.bun"

# Copiar archivos de requisitos primero para aprovechar caché de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para la base de datos y otros directorios necesarios
RUN mkdir -p /app/data /app/.web

# Exponer puerto que Railway espera
EXPOSE 8080

# Variables de entorno optimizadas para Railway
ENV PYTHONPATH=/app:/app/mi_app_estudio
ENV REFLEX_ENV=prod
ENV PORT=8080
ENV NODE_OPTIONS="--max-old-space-size=256"
ENV BUN_CONFIG_NO_CLEAR_TERMINAL=true
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar la aplicación (Railway usará Procfile si existe)
CMD ["python", "ultra_simple_start.py"]
# Dockerfile optimizado para Railway - SMART_STUDENT
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas (incluyendo unzip para Reflex)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements optimizado
COPY requirements.optimized.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Hacer el script ejecutable
RUN chmod +x railway_startup_optimized.sh

# Variables de entorno para Railway
ENV PYTHONPATH="/app"
ENV REFLEX_ENV="prod"
ENV NODE_ENV="production"
ENV PORT="8080"

# Exponer puerto
EXPOSE 8080

# Comando optimizado
CMD ["python", "railway_simple_start.py"]
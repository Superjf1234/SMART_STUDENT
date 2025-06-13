# Dockerfile ultra-simplificado para Railway
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Instalar Node.js (requerido por Reflex)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/.web

# Variables de entorno para Railway
ENV PYTHONPATH=/app:/app/mi_app_estudio
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["python", "railway_debug.py"]
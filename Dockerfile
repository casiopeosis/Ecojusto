FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema (si usas scipy/numpy necesitan estas)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY src/ ./src/
COPY frontend/ ./frontend/

# Puerto de Streamlit
EXPOSE 8501

# Variables de entorno opcionales
ENV PYTHONPATH=/app

CMD ["python3", "-m", "streamlit", "run", "src/frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
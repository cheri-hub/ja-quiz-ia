# API - Quiz de Perfumes
FROM python:3.13-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da API
COPY api/ .

# Copiar dados dos perfumes
COPY scrapper/perfumes.json /app/data/perfumes.json

# Expor porta
EXPOSE 8000

# Variáveis de ambiente padrão
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV PERFUMES_JSON_PATH=/app/data/perfumes.json

# Comando para iniciar
CMD ["python", "main.py"]

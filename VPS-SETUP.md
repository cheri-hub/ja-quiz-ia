# Configuração na VPS - JA Quiz de Perfumes

## 1. Criar pasta do projeto

```bash
mkdir -p /opt/ja-quiz
cd /opt/ja-quiz
```

## 2. Criar arquivo .env

```bash
cat > .env << 'EOF'
# Gemini AI
GEMINI_API_KEY=sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash
EOF
```

## 3. Criar docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
services:
  api:
    image: ghcr.io/cheri-hub/ja-quiz-ia-api:latest
    container_name: ja-quiz-api
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    image: ghcr.io/cheri-hub/ja-quiz-ia-web:latest
    container_name: ja-quiz-web
    ports:
      - "3000:80"
    depends_on:
      - api
    restart: unless-stopped
EOF
```

## 4. Login no GitHub Container Registry (se imagem privada)

```bash
echo "SEU_GITHUB_TOKEN" | docker login ghcr.io -u cheri-hub --password-stdin
```

## 5. Baixar imagens e iniciar

```bash
docker compose pull
docker compose up -d
```

## 6. Verificar status

```bash
docker compose ps
docker compose logs -f
```

## 7. Testar

```bash
# API
curl http://localhost:8000/health

# Web
curl http://localhost:3000
```

---

## Comandos úteis

```bash
# Parar
docker compose down

# Atualizar para nova versão
docker compose pull
docker compose up -d

# Ver logs
docker compose logs -f api
docker compose logs -f web

# Reiniciar
docker compose restart
```

## Portas usadas

| Serviço | Porta |
|---------|-------|
| API     | 8000  |
| Web     | 3000  |

## Nginx Reverse Proxy (opcional)

Se quiser usar domínio, adicione no nginx:

```nginx
server {
    listen 80;
    server_name quiz.seudominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        rewrite ^/api(.*)$ $1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

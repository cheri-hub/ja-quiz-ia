# 🎯 API Quiz de Perfumes - JA Essence de la Vie

API Backend para quiz de recomendação de perfumes usando **FastAPI** e **Google Gemini AI**.

## 📋 Funcionalidades

- 📝 **Quiz Interativo**: 10 perguntas para identificar o perfil olfativo
- 🤖 **IA Generativa**: Gemini AI analisa preferências e recomenda perfumes
- 🎯 **Top 3 Recomendações**: Melhores perfumes para cada perfil
- 📊 **Score de Compatibilidade**: Pontuação de match para cada recomendação
- 🔄 **Fallback Inteligente**: Sistema de regras quando Gemini não está disponível

## 🚀 Instalação

### 1. Instalar dependências

```bash
cd api
pip install -r requirements.txt
```

### 2. Configurar Gemini API (Opcional, mas recomendado)

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova API Key
3. Crie o arquivo `.env` na pasta `api/`:

```bash
# .env
GEMINI_API_KEY=sua_chave_api_gemini_aqui

# Server config (opcional)
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

> **Nota**: Sem a chave do Gemini, a API usará um sistema de regras como fallback.

### 3. Iniciar servidor

```bash
python main.py
```

O servidor iniciará em `http://localhost:8000`

## 📚 Endpoints

### Health Check
```
GET /health
```

Verifica status da API e configurações.

### Obter Perguntas do Quiz
```
GET /quiz/questions
```

Retorna todas as perguntas que devem ser exibidas ao usuário.

### Obter Recomendações
```
POST /quiz/recommend
Content-Type: application/json

{
    "genero": "masculino",        // masculino, feminino, unissex, qualquer
    "ocasiao": "noite",           // dia_a_dia, trabalho, noite, encontro, eventos_especiais, esportes
    "estacao": "inverno",         // verao, inverno, primavera, outono, qualquer
    "intensidade": "intensa",     // leve, moderada, intensa, muito_intensa
    "familia_olfativa": "amadeirado", // floral, amadeirado, citrico, oriental, frutado, fresco, gourmand, aromatico, nao_sei
    "personalidade": "sofisticado",   // classico, moderno, romantico, aventureiro, sofisticado, despojado, misterioso, energico
    "faixa_preco": "qualquer",    // ate_130, ate_150, ate_180, qualquer
    "notas_preferidas": ["baunilha", "âmbar"],  // opcional
    "notas_evitar": ["floral forte"],            // opcional
    "observacoes": "Procuro algo marcante"       // opcional
}
```

Retorna top 3 perfumes recomendados com score de match.

### Listar Perfumes
```
GET /perfumes
GET /perfumes?categoria=masculinos&limit=10
```

Lista todos os perfumes disponíveis.

### Buscar Perfume
```
GET /perfumes/{nome}
```

Busca um perfume específico por nome.

## 📖 Documentação Interativa

Acesse a documentação Swagger em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Estrutura

```
api/
├── main.py           # Aplicação FastAPI principal
├── models.py         # Modelos Pydantic (request/response)
├── gemini_service.py # Serviço de integração com Gemini AI
├── quiz_service.py   # Serviço com perguntas do quiz
├── requirements.txt  # Dependências Python
├── .env.example      # Exemplo de configuração
└── README.md         # Esta documentação
```

## 🔧 Tecnologias

- **FastAPI** - Framework web assíncrono
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados
- **Google Generative AI** - Gemini API
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📝 Exemplo de Resposta

```json
{
    "sucesso": true,
    "mensagem": "Recomendações geradas com Gemini AI!",
    "perfil_usuario": "Você busca fragrâncias amadeiradas e intensas...",
    "recomendacoes": [
        {
            "nome": "Cheval - Perfume Inspirado em Herod Parfums de Marly",
            "categoria": "masculinos",
            "preco": "R$134,90",
            "preco_pix": "R$170,90",
            "descricao": "Uma fragrância imponente e refinada...",
            "inspiracao": "Herod Parfums de Marly",
            "notas_fundo": "Baunilha, Cedro, Almíscar, Vetiver",
            "match_score": 95.0,
            "motivo_recomendacao": "Este perfume combina perfeitamente com seu perfil..."
        },
        // ... mais 2 perfumes
    ],
    "dica_extra": "Aplique nos pontos de pulsação para melhor projeção!"
}
```

## 🎨 Integração com Frontend

A API inclui CORS habilitado para todas as origens. Para uso em produção, configure as origens permitidas em `main.py`.

## 📄 Licença

Este projeto faz parte do ecossistema JA Essence de la Vie.

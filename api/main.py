"""
API de Quiz de Perfumes - JA Essence de la Vie
===============================================
Backend com integração Gemini AI para recomendação de perfumes
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models import (
    QuizAnswers, 
    QuizResult, 
    QuizQuestionsResponse,
    ErrorResponse,
    HealthCheck
)

# Limpar variáveis de ambiente antigas do sistema APENAS em desenvolvimento
# (não no Docker onde as variáveis vêm do docker-compose.yml)
if not os.path.exists("/.dockerenv"):
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("GOOGLE_API_KEY", None)

# Carregar variáveis de ambiente da raiz do projeto
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from gemini_service import gemini_service
from quiz_service import quiz_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    print("\n" + "="*50)
    print("🚀 Iniciando API de Quiz de Perfumes")
    print("="*50)
    print(f"✓ Perfumes carregados: {gemini_service.perfumes_count}")
    print(f"{'✓' if gemini_service.is_configured else '✗'} Gemini AI: {'Configurado' if gemini_service.is_configured else 'Não configurado (usando fallback)'}")
    print("="*50 + "\n")
    
    yield
    
    # Shutdown
    print("\n👋 Encerrando API...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Quiz de Perfumes - JA Essence de la Vie",
    description="""
    API para quiz de recomendação de perfumes usando Gemini AI.
    
    ## Funcionalidades
    
    * 📋 **Quiz Interativo**: Perguntas para identificar o perfil olfativo
    * 🤖 **IA Generativa**: Gemini AI analisa preferências e recomenda perfumes
    * 🎯 **Top 3 Recomendações**: Melhores perfumes para cada perfil
    * 📊 **Score de Compatibilidade**: Pontuação de match para cada recomendação
    
    ## Como usar
    
    1. Obtenha as perguntas do quiz via `GET /quiz/questions`
    2. Envie as respostas via `POST /quiz/recommend`
    3. Receba o top 3 de perfumes recomendados!
    """,
    version="1.0.0",
    contact={
        "name": "JA Essence de la Vie",
        "url": "https://www.jaessencedelavie.com.br",
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ ENDPOINTS ============

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "api": "Quiz de Perfumes - JA Essence de la Vie",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "quiz_questions": "/quiz/questions",
            "quiz_recommend": "/quiz/recommend",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Verifica o status da API"""
    return HealthCheck(
        status="ok",
        version="1.0.0",
        gemini_configured=gemini_service.is_configured,
        perfumes_loaded=gemini_service.perfumes_count
    )


@app.get(
    "/quiz/questions", 
    response_model=QuizQuestionsResponse,
    tags=["Quiz"],
    summary="Obter perguntas do quiz",
    description="Retorna todas as perguntas do quiz de perfumes para o frontend renderizar"
)
async def get_quiz_questions():
    """
    Retorna as perguntas do quiz de perfumes.
    
    Use esta rota para obter todas as perguntas que devem ser
    exibidas ao usuário antes de enviar as respostas.
    """
    return quiz_service.get_questions()


@app.post(
    "/quiz/recommend",
    response_model=QuizResult,
    responses={
        200: {"description": "Recomendações geradas com sucesso"},
        400: {"model": ErrorResponse, "description": "Erro nas respostas enviadas"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["Quiz"],
    summary="Obter recomendações de perfumes",
    description="Envia as respostas do quiz e recebe o top 3 de perfumes recomendados"
)
async def get_recommendations(answers: QuizAnswers):
    """
    Processa as respostas do quiz e retorna recomendações.
    
    A IA Gemini analisa as preferências do usuário e seleciona
    os 3 perfumes mais compatíveis do catálogo.
    
    Se o Gemini não estiver configurado, usa sistema de regras como fallback.
    """
    try:
        result = await gemini_service.get_recommendations(answers)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar recomendações: {str(e)}"
        )


@app.get(
    "/perfumes",
    tags=["Perfumes"],
    summary="Listar todos os perfumes",
    description="Retorna a lista completa de perfumes disponíveis"
)
async def list_perfumes(
    categoria: str = None,
    limit: int = 50
):
    """
    Lista todos os perfumes do catálogo.
    
    - **categoria**: Filtrar por categoria (compartilhaveis, masculinos, femininos)
    - **limit**: Limite de resultados (padrão: 50)
    """
    perfumes = gemini_service.perfumes_data
    
    if categoria:
        perfumes = [p for p in perfumes if p.get("categoria") == categoria]
    
    return {
        "total": len(perfumes),
        "perfumes": perfumes[:limit]
    }


@app.get(
    "/perfumes/{nome}",
    tags=["Perfumes"],
    summary="Buscar perfume por nome",
    description="Busca um perfume específico pelo nome (busca parcial)"
)
async def get_perfume(nome: str):
    """
    Busca um perfume pelo nome.
    
    A busca é case-insensitive e aceita correspondência parcial.
    """
    perfume = gemini_service._find_perfume(nome)
    
    if not perfume:
        raise HTTPException(
            status_code=404,
            detail=f"Perfume '{nome}' não encontrado"
        )
    
    return perfume


# ============ ERROR HANDLERS ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "sucesso": False,
            "erro": exc.detail,
            "detalhes": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "sucesso": False,
            "erro": "Erro interno do servidor",
            "detalhes": str(exc)
        }
    )


# ============ MAIN ============

if __name__ == "__main__":
    import sys
    import uvicorn
    
    # Desabilitar geração de arquivos .pyc para o processo e subprocessos
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"\n🌐 Servidor iniciando em http://{host}:{port}")
    print(f"📚 Documentação: http://{host}:{port}/docs\n")
    
    # Configuração do reload - apenas arquivos .py no diretório atual
    reload_config = {
        "reload": debug,
        "reload_includes": ["*.py"],
        "reload_excludes": ["**/__pycache__/**"]
    } if debug else {"reload": False}
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        **reload_config
    )

"""
Modelos Pydantic para a API de Quiz de Perfumes
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class Genero(str, Enum):
    MASCULINO = "masculino"
    FEMININO = "feminino"
    UNISSEX = "unissex"
    QUALQUER = "qualquer"


class Ocasiao(str, Enum):
    DIA_A_DIA = "dia_a_dia"
    TRABALHO = "trabalho"
    NOITE = "noite"
    ENCONTRO = "encontro"
    EVENTOS_ESPECIAIS = "eventos_especiais"
    ESPORTES = "esportes"


class Estacao(str, Enum):
    VERAO = "verao"
    INVERNO = "inverno"
    PRIMAVERA = "primavera"
    OUTONO = "outono"
    QUALQUER = "qualquer"


class Intensidade(str, Enum):
    LEVE = "leve"
    MODERADA = "moderada"
    INTENSA = "intensa"
    MUITO_INTENSA = "muito_intensa"


class FamiliaOlfativa(str, Enum):
    FLORAL = "floral"
    AMADEIRADO = "amadeirado"
    CITRICO = "citrico"
    ORIENTAL = "oriental"
    FRUTADO = "frutado"
    FRESCO = "fresco"
    GOURMAND = "gourmand"
    AROMATICO = "aromatico"
    NAO_SEI = "nao_sei"


class Personalidade(str, Enum):
    CLASSICO = "classico"
    MODERNO = "moderno"
    ROMANTICO = "romantico"
    AVENTUREIRO = "aventureiro"
    SOFISTICADO = "sofisticado"
    DESPOJADO = "despojado"
    MISTERIOSO = "misterioso"
    ENERGICO = "energico"


class FaixaPreco(str, Enum):
    ATE_130 = "ate_130"
    ATE_150 = "ate_150"
    ATE_180 = "ate_180"
    QUALQUER = "qualquer"


# ============ REQUEST MODELS ============

class QuizAnswers(BaseModel):
    """Respostas do quiz de perfumes"""
    genero: Genero = Field(..., description="Gênero do perfume desejado")
    ocasiao: Ocasiao = Field(..., description="Principal ocasião de uso")
    estacao: Estacao = Field(..., description="Estação preferida para uso")
    intensidade: Intensidade = Field(..., description="Intensidade desejada")
    familia_olfativa: FamiliaOlfativa = Field(..., description="Família olfativa preferida")
    personalidade: Personalidade = Field(..., description="Personalidade que deseja transmitir")
    faixa_preco: FaixaPreco = Field(default=FaixaPreco.QUALQUER, description="Faixa de preço")
    notas_preferidas: Optional[List[str]] = Field(default=None, description="Notas olfativas preferidas")
    notas_evitar: Optional[List[str]] = Field(default=None, description="Notas a evitar")
    observacoes: Optional[str] = Field(default=None, description="Observações adicionais")

    class Config:
        json_schema_extra = {
            "example": {
                "genero": "masculino",
                "ocasiao": "noite",
                "estacao": "inverno",
                "intensidade": "intensa",
                "familia_olfativa": "amadeirado",
                "personalidade": "sofisticado",
                "faixa_preco": "qualquer",
                "notas_preferidas": ["baunilha", "âmbar"],
                "notas_evitar": ["floral forte"],
                "observacoes": "Procuro algo marcante para ocasiões especiais"
            }
        }


# ============ RESPONSE MODELS ============

class Comentario(BaseModel):
    """Comentário de um perfume"""
    data: Optional[str] = None
    autor: str
    comentario: str
    verificado: bool = False


class PerfumeRecomendado(BaseModel):
    """Perfume recomendado pelo quiz"""
    nome: str
    categoria: str
    preco: Optional[str] = None
    preco_pix: Optional[str] = None
    preco_original: Optional[str] = None
    parcelamento: Optional[str] = None
    descricao: Optional[str] = None
    inspiracao: Optional[str] = None
    volume: Optional[str] = None
    notas_topo: Optional[str] = None
    notas_coracao: Optional[str] = None
    notas_fundo: Optional[str] = None
    imagem_url: Optional[str] = None
    link_produto: Optional[str] = None
    desconto: Optional[str] = None
    match_score: float = Field(..., description="Pontuação de compatibilidade (0-100)")
    motivo_recomendacao: str = Field(..., description="Motivo da recomendação pela IA")


class QuizResult(BaseModel):
    """Resultado do quiz com top 3 perfumes"""
    sucesso: bool = True
    mensagem: str = "Recomendações geradas com sucesso!"
    perfil_usuario: str = Field(..., description="Descrição do perfil olfativo do usuário")
    recomendacoes: List[PerfumeRecomendado] = Field(..., description="Top 3 perfumes recomendados")
    dica_extra: Optional[str] = Field(default=None, description="Dica adicional da IA")


class QuizQuestion(BaseModel):
    """Pergunta do quiz"""
    id: str
    pergunta: str
    descricao: Optional[str] = None
    tipo: str  # "select", "multiselect", "text"
    opcoes: Optional[List[dict]] = None
    obrigatoria: bool = True


class QuizQuestionsResponse(BaseModel):
    """Resposta com todas as perguntas do quiz"""
    titulo: str = "Quiz de Perfumes - JA Essence de la Vie"
    descricao: str = "Descubra o perfume ideal para você!"
    perguntas: List[QuizQuestion]


class ErrorResponse(BaseModel):
    """Resposta de erro"""
    sucesso: bool = False
    erro: str
    detalhes: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str = "1.0.0"
    gemini_configured: bool = False
    perfumes_loaded: int = 0

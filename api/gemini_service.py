"""
Serviço de integração com Google Gemini para recomendações de perfumes
"""
import os
import json
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from google import genai
from dotenv import load_dotenv

from models import QuizAnswers, PerfumeRecomendado, QuizResult

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gemini_service")

# Carregar variáveis de ambiente da raiz do projeto
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class GeminiService:
    """Serviço para interação com Gemini AI"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.perfumes_data: List[Dict] = []
        self._configure()
        self._load_perfumes()
    
    def _configure(self):
        """Configura a API do Gemini"""
        # Limpar a chave de espaços em branco
        self.api_key = self.api_key.strip() if self.api_key else None
        
        logger.info(f"Configurando Gemini - API Key presente: {bool(self.api_key)}")
        logger.info(f"Modelo configurado: {self.model_name}")
        logger.info(f"Tamanho da API Key: {len(self.api_key) if self.api_key else 0}")
        
        if self.api_key and self.api_key != "sua_chave_api_gemini_aqui":
            # Configurar como GOOGLE_API_KEY para o SDK usar
            os.environ["GOOGLE_API_KEY"] = self.api_key
            self.client = genai.Client(api_key=self.api_key)
            logger.info("✓ Cliente Gemini criado com sucesso")
        else:
            logger.warning("⚠ API Key não configurada ou inválida")
    
    def _load_perfumes(self):
        """Carrega os dados dos perfumes do JSON"""
        # Usar variável de ambiente ou caminho relativo padrão
        env_path = os.getenv("PERFUMES_JSON_PATH")
        if env_path:
            perfumes_path = Path(env_path)
        else:
            perfumes_path = Path(__file__).parent.parent / "scrapper" / "perfumes.json"
        
        if perfumes_path.exists():
            with open(perfumes_path, "r", encoding="utf-8") as f:
                self.perfumes_data = json.load(f)
            print(f"✓ Carregados {len(self.perfumes_data)} perfumes")
        else:
            print(f"⚠ Arquivo perfumes.json não encontrado em {perfumes_path}")
    
    @property
    def is_configured(self) -> bool:
        """Verifica se o Gemini está configurado"""
        return self.client is not None
    
    @property
    def perfumes_count(self) -> int:
        """Retorna a quantidade de perfumes carregados"""
        return len(self.perfumes_data)
    
    def _build_perfumes_context(self) -> str:
        """Constrói o contexto dos perfumes para o prompt"""
        context_lines = []
        
        for i, p in enumerate(self.perfumes_data, 1):
            notas = []
            if p.get("notas_topo"):
                notas.append(f"Topo: {p['notas_topo']}")
            if p.get("notas_coracao"):
                notas.append(f"Coração: {p['notas_coracao']}")
            if p.get("notas_fundo"):
                notas.append(f"Fundo: {p['notas_fundo']}")
            
            notas_str = " | ".join(notas) if notas else "Não informado"
            
            preco = p.get("preco_pix") or p.get("preco") or "Não informado"
            
            # Garantir que descrição não seja None
            descricao = p.get("descricao") or "Não informado"
            descricao = descricao[:200] if descricao else "Não informado"
            
            context_lines.append(
                f"{i}. {p['nome']}\n"
                f"   Categoria: {p['categoria']}\n"
                f"   Preço: {preco}\n"
                f"   Inspirado em: {p.get('inspiracao') or 'Não informado'}\n"
                f"   Notas: {notas_str}\n"
                f"   Descrição: {descricao}"
            )
        
        return "\n\n".join(context_lines)
    
    def _build_quiz_context(self, answers: QuizAnswers) -> str:
        """Constrói o contexto das respostas do quiz"""
        context = f"""
RESPOSTAS DO QUIZ:
- Gênero preferido: {answers.genero.value}
- Ocasião principal: {answers.ocasiao.value.replace('_', ' ')}
- Estação do ano: {answers.estacao.value}
- Intensidade desejada: {answers.intensidade.value.replace('_', ' ')}
- Família olfativa: {answers.familia_olfativa.value.replace('_', ' ')}
- Personalidade: {answers.personalidade.value}
- Faixa de preço: {answers.faixa_preco.value.replace('_', ' ')}
"""
        
        if answers.notas_preferidas:
            context += f"- Notas preferidas: {', '.join(answers.notas_preferidas)}\n"
        
        if answers.notas_evitar:
            context += f"- Notas a evitar: {', '.join(answers.notas_evitar)}\n"
        
        if answers.observacoes:
            context += f"- Observações adicionais: {answers.observacoes}\n"
        
        return context
    
    async def get_recommendations(self, answers: QuizAnswers) -> QuizResult:
        """Obtém recomendações de perfumes baseadas nas respostas do quiz"""
        
        logger.info("="*50)
        logger.info("INICIANDO get_recommendations")
        logger.info(f"is_configured: {self.is_configured}")
        logger.info(f"client: {self.client}")
        logger.info(f"model_name: {self.model_name}")
        logger.info(f"api_key (primeiros 10 chars): {self.api_key[:10] if self.api_key else 'None'}...")
        
        if not self.is_configured:
            logger.warning("Gemini NÃO configurado - usando fallback")
            # Fallback: recomendação baseada em regras simples
            return self._fallback_recommendations(answers)
        
        logger.info("Gemini está configurado, gerando recomendação via IA...")
        quiz_context = self._build_quiz_context(answers)
        perfumes_context = self._build_perfumes_context()
        
        prompt = f"""Você é um especialista em perfumaria e consultor de fragrâncias da JA Essence de la Vie.
Analise as preferências do usuário e recomende os 3 melhores perfumes do nosso catálogo.

{quiz_context}

CATÁLOGO DE PERFUMES DISPONÍVEIS:
{perfumes_context}

INSTRUÇÕES:
1. Analise cuidadosamente o perfil do usuário baseado nas respostas
2. Selecione EXATAMENTE 3 perfumes do catálogo que melhor combinam com o perfil
3. Para cada perfume, forneça uma pontuação de 0 a 100 e o motivo da recomendação
4. Crie uma descrição do perfil olfativo do usuário
5. Adicione uma dica extra sobre uso de perfumes

IMPORTANTE: 
- Use APENAS perfumes que existem no catálogo fornecido
- Os nomes dos perfumes devem ser EXATAMENTE iguais aos do catálogo
- Considere categoria (masculino/feminino/compartilhavel) conforme preferência do usuário
- Se gênero for "qualquer", priorize compartilháveis

RESPONDA APENAS EM JSON válido no seguinte formato (sem markdown):
{{
    "perfil_usuario": "Descrição do perfil olfativo do usuário em 2-3 frases",
    "recomendacoes": [
        {{
            "nome_perfume": "Nome exato do perfume do catálogo",
            "match_score": 95,
            "motivo_recomendacao": "Explicação de por que este perfume combina com o perfil"
        }},
        {{
            "nome_perfume": "Nome do segundo perfume",
            "match_score": 88,
            "motivo_recomendacao": "Explicação"
        }},
        {{
            "nome_perfume": "Nome do terceiro perfume",
            "match_score": 82,
            "motivo_recomendacao": "Explicação"
        }}
    ],
    "dica_extra": "Uma dica útil sobre perfumes"
}}"""

        try:
            logger.info(f"Chamando Gemini API - modelo: {self.model_name}")
            logger.debug(f"Tamanho do prompt: {len(prompt)} caracteres")
            logger.debug(f"self.model_name: {self.model_name}")
            
            # Tentar gerar conteúdo
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            )
            
            logger.info(f"Resposta recebida do Gemini")
            logger.debug(f"Tipo da resposta: {type(response)}")
            
            # Verificar se a resposta tem texto
            if not response or not response.text:
                logger.warning("Gemini retornou resposta vazia, usando fallback")
                return self._fallback_recommendations(answers)
            
            result_text = response.text.strip()
            logger.info(f"Texto recebido ({len(result_text)} chars): {result_text[:200]}...")
            
            # Limpar resposta (remover markdown se presente)
            if result_text.startswith("```"):
                result_text = re.sub(r"```json?\n?", "", result_text)
                result_text = re.sub(r"\n?```$", "", result_text)
            
            result_json = json.loads(result_text)
            
            # Mapear recomendações para objetos PerfumeRecomendado
            recomendacoes = []
            for rec in result_json.get("recomendacoes", [])[:3]:
                nome_perfume = rec.get("nome_perfume", "")
                
                # Encontrar perfume no catálogo
                perfume_data = self._find_perfume(nome_perfume)
                
                if perfume_data:
                    recomendacoes.append(PerfumeRecomendado(
                        nome=perfume_data["nome"],
                        categoria=perfume_data.get("categoria", ""),
                        preco=perfume_data.get("preco"),
                        preco_pix=perfume_data.get("preco_pix"),
                        preco_original=perfume_data.get("preco_original"),
                        parcelamento=perfume_data.get("parcelamento"),
                        descricao=perfume_data.get("descricao"),
                        inspiracao=perfume_data.get("inspiracao"),
                        volume=perfume_data.get("volume"),
                        notas_topo=perfume_data.get("notas_topo"),
                        notas_coracao=perfume_data.get("notas_coracao"),
                        notas_fundo=perfume_data.get("notas_fundo"),
                        imagem_url=perfume_data.get("imagem_url"),
                        link_produto=perfume_data.get("link_produto"),
                        desconto=perfume_data.get("desconto"),
                        match_score=float(rec.get("match_score", 80)),
                        motivo_recomendacao=rec.get("motivo_recomendacao", "")
                    ))
            
            # Se não encontrou 3.perfumes, completar com fallback
            if len(recomendacoes) < 3:
                fallback = self._fallback_recommendations(answers)
                for fb_rec in fallback.recomendacoes:
                    if len(recomendacoes) >= 3:
                        break
                    if not any(r.nome == fb_rec.nome for r in recomendacoes):
                        recomendacoes.append(fb_rec)
            
            logger.info("✓ Recomendações geradas com sucesso via Gemini AI!")
            return QuizResult(
                sucesso=True,
                mensagem="Recomendações geradas com Gemini AI!",
                perfil_usuario=result_json.get("perfil_usuario", "Perfil olfativo personalizado"),
                recomendacoes=recomendacoes[:3],
                dica_extra=result_json.get("dica_extra")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON do Gemini: {e}")
            try:
                logger.error(f"Resposta recebida: {result_text[:500] if result_text else 'vazia'}")
            except:
                pass
            return self._fallback_recommendations(answers)
        except Exception as e:
            logger.error(f"Erro na API Gemini: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._fallback_recommendations(answers)
    
    def _find_perfume(self, nome: str) -> Optional[Dict]:
        """Encontra um perfume pelo nome (busca flexível)"""
        nome_lower = nome.lower().strip()
        
        # Busca exata
        for p in self.perfumes_data:
            if p["nome"].lower() == nome_lower:
                return p
        
        # Busca parcial (nome contém)
        for p in self.perfumes_data:
            if nome_lower in p["nome"].lower() or p["nome"].lower() in nome_lower:
                return p
        
        # Busca por palavras-chave
        palavras = nome_lower.split()
        for p in self.perfumes_data:
            nome_perfume = p["nome"].lower()
            if any(palavra in nome_perfume for palavra in palavras if len(palavra) > 3):
                return p
        
        return None
    
    def _fallback_recommendations(self, answers: QuizAnswers) -> QuizResult:
        """Recomendações baseadas em regras quando Gemini não está disponível"""
        logger.warning("="*50)
        logger.warning("USANDO FALLBACK - Gemini não disponível ou falhou")
        logger.warning("="*50)
        
        # Filtrar por categoria
        categoria_map = {
            "masculino": "masculinos",
            "feminino": "femininos",
            "unissex": "compartilhaveis",
            "qualquer": None
        }
        categoria = categoria_map.get(answers.genero.value)
        
        candidatos = []
        for p in self.perfumes_data:
            score = 50  # Score base
            
            # Filtro de categoria
            if categoria and p.get("categoria") != categoria:
                if answers.genero.value != "qualquer":
                    score -= 20
            elif categoria and p.get("categoria") == categoria:
                score += 20
            
            # Bonus por descrição matching
            descricao = (p.get("descricao") or "").lower()
            notas = " ".join([
                p.get("notas_topo") or "",
                p.get("notas_coracao") or "",
                p.get("notas_fundo") or ""
            ]).lower()
            
            keywords_map = {
                "floral": ["floral", "rosa", "jasmim", "lírio", "flor"],
                "amadeirado": ["amadeirado", "madeira", "cedro", "sândalo", "vetiver"],
                "citrico": ["cítrico", "limão", "bergamota", "laranja", "citrus"],
                "oriental": ["oriental", "âmbar", "incenso", "especiado", "oud"],
                "frutado": ["frutado", "frutas", "maçã", "pêssego", "cereja"],
                "fresco": ["fresco", "aquático", "marinho", "refrescante"],
                "gourmand": ["gourmand", "baunilha", "caramelo", "chocolate", "doce"],
                "aromatico": ["aromático", "herbal", "lavanda", "alecrim"]
            }
            
            familia = answers.familia_olfativa.value
            if familia in keywords_map:
                for keyword in keywords_map[familia]:
                    if keyword in descricao or keyword in notas:
                        score += 10
            
            # Bonus por intensidade (baseado em descrição)
            if answers.intensidade.value in ["intensa", "muito_intensa"]:
                if any(w in descricao for w in ["intenso", "marcante", "potente", "forte"]):
                    score += 10
            elif answers.intensidade.value == "leve":
                if any(w in descricao for w in ["leve", "suave", "delicado", "sutil"]):
                    score += 10
            
            # Bonus por personalidade
            personalidade_keywords = {
                "sofisticado": ["elegância", "sofisticação", "refinado", "luxo"],
                "romantico": ["romântico", "sedutor", "sensual", "apaixonado"],
                "aventureiro": ["aventura", "energia", "vibrante", "ousado"],
                "misterioso": ["mistério", "enigmático", "profundo", "noturno"],
                "classico": ["clássico", "atemporal", "tradicional"],
                "moderno": ["moderno", "contemporâneo", "atual"],
                "despojado": ["casual", "despojado", "leve", "fresco"],
                "energico": ["energia", "vibrante", "dinâmico", "explosivo"]
            }
            
            if answers.personalidade.value in personalidade_keywords:
                for keyword in personalidade_keywords[answers.personalidade.value]:
                    if keyword in descricao:
                        score += 8
            
            candidatos.append((p, min(score, 100)))
        
        # Ordenar por score
        candidatos.sort(key=lambda x: x[1], reverse=True)
        
        # Selecionar top 3
        recomendacoes = []
        for p, score in candidatos[:3]:
            motivo = self._generate_fallback_reason(p, answers)
            recomendacoes.append(PerfumeRecomendado(
                nome=p["nome"],
                categoria=p.get("categoria", ""),
                preco=p.get("preco"),
                preco_pix=p.get("preco_pix"),
                preco_original=p.get("preco_original"),
                parcelamento=p.get("parcelamento"),
                descricao=p.get("descricao"),
                inspiracao=p.get("inspiracao"),
                volume=p.get("volume"),
                notas_topo=p.get("notas_topo"),
                notas_coracao=p.get("notas_coracao"),
                notas_fundo=p.get("notas_fundo"),
                imagem_url=p.get("imagem_url"),
                link_produto=p.get("link_produto"),
                desconto=p.get("desconto"),
                match_score=float(score),
                motivo_recomendacao=motivo
            ))
        
        perfil = f"Você busca fragrâncias {answers.familia_olfativa.value} com intensidade {answers.intensidade.value}. "
        perfil += f"Sua personalidade {answers.personalidade.value} combina bem com perfumes marcantes para {answers.ocasiao.value.replace('_', ' ')}."
        
        return QuizResult(
            sucesso=True,
            mensagem="Recomendações baseadas em análise de compatibilidade",
            perfil_usuario=perfil,
            recomendacoes=recomendacoes,
            dica_extra="Aplique o perfume nos pontos de pulsação (pulsos, pescoço) para melhor projeção!"
        )
    
    def _generate_fallback_reason(self, perfume: Dict, answers: QuizAnswers) -> str:
        """Gera um motivo de recomendação baseado em regras"""
        reasons = []
        
        if perfume.get("categoria") == "compartilhaveis":
            reasons.append("versátil para qualquer ocasião")
        elif perfume.get("categoria") == answers.genero.value + "s":
            reasons.append(f"ideal para o público {answers.genero.value}")
        
        if perfume.get("inspiracao"):
            reasons.append(f"inspirado na renomada fragrância {perfume['inspiracao']}")
        
        if perfume.get("descricao"):
            desc = perfume["descricao"].lower()
            if "elegância" in desc or "sofisticação" in desc:
                reasons.append("transmite elegância e sofisticação")
            if "fresco" in desc or "refrescante" in desc:
                reasons.append("oferece frescor agradável")
            if "intenso" in desc or "marcante" in desc:
                reasons.append("possui presença marcante")
        
        if not reasons:
            reasons.append("excelente opção para o seu perfil")
        
        return "Este perfume é " + ", ".join(reasons) + "."


# Instância global do serviço
gemini_service = GeminiService()

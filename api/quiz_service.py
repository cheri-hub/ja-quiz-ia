"""
Serviço do Quiz de Perfumes
"""
from typing import List
from models import QuizQuestion, QuizQuestionsResponse


class QuizService:
    """Serviço para gerenciar as perguntas do quiz"""
    
    @staticmethod
    def get_questions() -> QuizQuestionsResponse:
        """Retorna todas as perguntas do quiz"""
        
        perguntas = [
            QuizQuestion(
                id="genero",
                pergunta="Para quem é o perfume?",
                descricao="Escolha o gênero do perfume que você procura",
                tipo="select",
                opcoes=[
                    {"valor": "masculino", "label": "Masculino", "emoji": "👔"},
                    {"valor": "feminino", "label": "Feminino", "emoji": "👗"},
                    {"valor": "unissex", "label": "Unissex / Compartilhável", "emoji": "🌟"},
                    {"valor": "qualquer", "label": "Não tenho preferência", "emoji": "✨"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="ocasiao",
                pergunta="Para qual ocasião você mais usará o perfume?",
                descricao="A ocasião ajuda a definir a intensidade e estilo ideal",
                tipo="select",
                opcoes=[
                    {"valor": "dia_a_dia", "label": "Dia a dia casual", "emoji": "☀️"},
                    {"valor": "trabalho", "label": "Trabalho / Escritório", "emoji": "💼"},
                    {"valor": "noite", "label": "Noite / Baladas", "emoji": "🌙"},
                    {"valor": "encontro", "label": "Encontros românticos", "emoji": "❤️"},
                    {"valor": "eventos_especiais", "label": "Eventos especiais / Festas", "emoji": "🎉"},
                    {"valor": "esportes", "label": "Esportes / Atividades físicas", "emoji": "🏃"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="estacao",
                pergunta="Em qual estação você pretende usar mais?",
                descricao="A temperatura influencia na performance do perfume",
                tipo="select",
                opcoes=[
                    {"valor": "verao", "label": "Verão", "emoji": "🌞", "descricao": "Prefira fragrâncias frescas e leves"},
                    {"valor": "inverno", "label": "Inverno", "emoji": "❄️", "descricao": "Fragrâncias mais intensas funcionam melhor"},
                    {"valor": "primavera", "label": "Primavera", "emoji": "🌸", "descricao": "Florais e frutados são ótimas opções"},
                    {"valor": "outono", "label": "Outono", "emoji": "🍂", "descricao": "Amadeirados e especiados combinam bem"},
                    {"valor": "qualquer", "label": "Uso o ano todo", "emoji": "📅"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="intensidade",
                pergunta="Qual intensidade você prefere?",
                descricao="Define o quão marcante será a fragrância",
                tipo="select",
                opcoes=[
                    {"valor": "leve", "label": "Leve", "emoji": "🍃", "descricao": "Sutil, para quem prefere discrição"},
                    {"valor": "moderada", "label": "Moderada", "emoji": "💨", "descricao": "Equilibrada, perceptível mas não exagerada"},
                    {"valor": "intensa", "label": "Intensa", "emoji": "💥", "descricao": "Marcante, deixa rastro por onde passa"},
                    {"valor": "muito_intensa", "label": "Muito intensa", "emoji": "🔥", "descricao": "Para fazer presença e ser notado"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="familia_olfativa",
                pergunta="Qual família olfativa mais te atrai?",
                descricao="A base do perfume que define sua característica principal",
                tipo="select",
                opcoes=[
                    {"valor": "floral", "label": "Floral", "emoji": "🌹", "descricao": "Rosa, jasmim, lírio, violeta"},
                    {"valor": "amadeirado", "label": "Amadeirado", "emoji": "🪵", "descricao": "Cedro, sândalo, vetiver, oud"},
                    {"valor": "citrico", "label": "Cítrico", "emoji": "🍋", "descricao": "Limão, bergamota, laranja, toranja"},
                    {"valor": "oriental", "label": "Oriental / Especiado", "emoji": "🕌", "descricao": "Âmbar, incenso, baunilha, especiarias"},
                    {"valor": "frutado", "label": "Frutado", "emoji": "🍑", "descricao": "Pêssego, maçã, frutas vermelhas"},
                    {"valor": "fresco", "label": "Fresco / Aquático", "emoji": "🌊", "descricao": "Notas marinhas, ozônicas, refrescantes"},
                    {"valor": "gourmand", "label": "Gourmand", "emoji": "🍫", "descricao": "Baunilha, caramelo, chocolate, café"},
                    {"valor": "aromatico", "label": "Aromático / Herbal", "emoji": "🌿", "descricao": "Lavanda, alecrim, hortelã, sálvia"},
                    {"valor": "nao_sei", "label": "Não sei / Me surpreenda!", "emoji": "🎁"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="personalidade",
                pergunta="Qual personalidade você quer transmitir?",
                descricao="O perfume pode comunicar muito sobre você",
                tipo="select",
                opcoes=[
                    {"valor": "classico", "label": "Clássico / Elegante", "emoji": "👑", "descricao": "Atemporal e refinado"},
                    {"valor": "moderno", "label": "Moderno / Contemporâneo", "emoji": "🆕", "descricao": "Atual e inovador"},
                    {"valor": "romantico", "label": "Romântico / Sedutor", "emoji": "💕", "descricao": "Sensual e envolvente"},
                    {"valor": "aventureiro", "label": "Aventureiro / Ousado", "emoji": "🏔️", "descricao": "Destemido e marcante"},
                    {"valor": "sofisticado", "label": "Sofisticado / Luxuoso", "emoji": "💎", "descricao": "Exclusivo e premium"},
                    {"valor": "despojado", "label": "Despojado / Casual", "emoji": "😎", "descricao": "Leve e descontraído"},
                    {"valor": "misterioso", "label": "Misterioso / Enigmático", "emoji": "🌑", "descricao": "Intrigante e profundo"},
                    {"valor": "energico", "label": "Energético / Vibrante", "emoji": "⚡", "descricao": "Dinâmico e cheio de vida"}
                ],
                obrigatoria=True
            ),
            
            QuizQuestion(
                id="faixa_preco",
                pergunta="Qual sua faixa de preço?",
                descricao="Todos os nossos perfumes oferecem excelente custo-benefício",
                tipo="select",
                opcoes=[
                    {"valor": "ate_130", "label": "Até R$ 130", "emoji": "💰"},
                    {"valor": "ate_150", "label": "Até R$ 150", "emoji": "💵"},
                    {"valor": "ate_180", "label": "Até R$ 180", "emoji": "💳"},
                    {"valor": "qualquer", "label": "Qualquer valor", "emoji": "✨"}
                ],
                obrigatoria=False
            ),
            
            QuizQuestion(
                id="notas_preferidas",
                pergunta="Tem alguma nota olfativa que você adora?",
                descricao="Opcional - selecione suas notas favoritas",
                tipo="multiselect",
                opcoes=[
                    {"valor": "baunilha", "label": "Baunilha"},
                    {"valor": "ambar", "label": "Âmbar"},
                    {"valor": "almiscar", "label": "Almíscar"},
                    {"valor": "cedro", "label": "Cedro"},
                    {"valor": "sandalo", "label": "Sândalo"},
                    {"valor": "rosa", "label": "Rosa"},
                    {"valor": "jasmim", "label": "Jasmim"},
                    {"valor": "lavanda", "label": "Lavanda"},
                    {"valor": "bergamota", "label": "Bergamota"},
                    {"valor": "oud", "label": "Oud / Madeira de Ágar"},
                    {"valor": "patchouli", "label": "Patchouli"},
                    {"valor": "vetiver", "label": "Vetiver"},
                    {"valor": "cafe", "label": "Café"},
                    {"valor": "caramelo", "label": "Caramelo"},
                    {"valor": "frutas", "label": "Frutas em geral"}
                ],
                obrigatoria=False
            ),
            
            QuizQuestion(
                id="notas_evitar",
                pergunta="Tem alguma nota que você NÃO gosta?",
                descricao="Opcional - evitaremos perfumes com essas notas",
                tipo="multiselect",
                opcoes=[
                    {"valor": "floral_forte", "label": "Florais fortes"},
                    {"valor": "oud", "label": "Oud / Notas muito amadeiradas"},
                    {"valor": "incenso", "label": "Incenso"},
                    {"valor": "patchouli", "label": "Patchouli"},
                    {"valor": "almiscar", "label": "Almíscar forte"},
                    {"valor": "doces", "label": "Notas muito doces"},
                    {"valor": "citricos", "label": "Cítricos fortes"},
                    {"valor": "especiarias", "label": "Especiarias"}
                ],
                obrigatoria=False
            ),
            
            QuizQuestion(
                id="observacoes",
                pergunta="Alguma observação adicional?",
                descricao="Opcional - conte mais sobre o que você busca",
                tipo="text",
                opcoes=None,
                obrigatoria=False
            )
        ]
        
        return QuizQuestionsResponse(
            titulo="Quiz de Perfumes - JA Essence de la Vie",
            descricao="Responda algumas perguntas e descubra o perfume ideal para você! Nossa IA irá analisar suas preferências e recomendar as melhores opções do nosso catálogo.",
            perguntas=perguntas
        )


# Instância global
quiz_service = QuizService()

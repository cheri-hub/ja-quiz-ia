// Types que espelham os modelos da API

export type Genero = "masculino" | "feminino" | "unissex" | "qualquer";
export type Ocasiao = "dia_a_dia" | "trabalho" | "noite" | "encontro" | "eventos_especiais" | "esportes";
export type Estacao = "verao" | "inverno" | "primavera" | "outono" | "qualquer";
export type Intensidade = "leve" | "moderada" | "intensa" | "muito_intensa";
export type FamiliaOlfativa = "floral" | "amadeirado" | "citrico" | "oriental" | "frutado" | "fresco" | "gourmand" | "aromatico" | "nao_sei";
export type Personalidade = "classico" | "moderno" | "romantico" | "aventureiro" | "sofisticado" | "despojado" | "misterioso" | "energico";
export type FaixaPreco = "ate_130" | "ate_150" | "ate_180" | "qualquer";

export interface QuizAnswers {
  genero: Genero;
  ocasiao: Ocasiao;
  estacao: Estacao;
  intensidade: Intensidade;
  familia_olfativa: FamiliaOlfativa;
  personalidade: Personalidade;
  faixa_preco: FaixaPreco;
  notas_preferidas?: string[];
  notas_evitar?: string[];
  observacoes?: string;
}

export interface QuizOption {
  valor: string;
  label: string;
  emoji?: string;
  descricao?: string;
}

export interface QuizQuestion {
  id: string;
  pergunta: string;
  descricao?: string;
  tipo: "select" | "multiselect" | "text";
  opcoes?: QuizOption[];
  obrigatoria: boolean;
}

export interface QuizQuestionsResponse {
  titulo: string;
  descricao: string;
  perguntas: QuizQuestion[];
}

export interface Comentario {
  data?: string;
  autor: string;
  comentario: string;
  verificado: boolean;
}

export interface PerfumeRecomendado {
  nome: string;
  categoria: string;
  preco?: string;
  preco_pix?: string;
  preco_original?: string;
  parcelamento?: string;
  descricao?: string;
  inspiracao?: string;
  volume?: string;
  notas_topo?: string;
  notas_coracao?: string;
  notas_fundo?: string;
  imagem_url?: string;
  link_produto?: string;
  desconto?: string;
  match_score: number;
  motivo_recomendacao: string;
}

export interface QuizResult {
  sucesso: boolean;
  mensagem: string;
  perfil_usuario: string;
  recomendacoes: PerfumeRecomendado[];
  dica_extra?: string;
}

export interface ErrorResponse {
  sucesso: boolean;
  erro: string;
  detalhes?: string;
}

import type { QuizResult } from "../types";
import { PerfumeCard } from "./PerfumeCard";

interface ResultsDisplayProps {
  result: QuizResult;
  onRestart: () => void;
}

export function ResultsDisplay({ result, onRestart }: ResultsDisplayProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-800">🎉 Seus Perfumes Ideais!</h1>
        <p className="text-gray-600 mt-2">{result.mensagem}</p>
      </div>

      {/* Perfil do usuário */}
      <div className="bg-gradient-to-r from-purple-100 to-pink-100 p-5 rounded-xl">
        <h2 className="font-semibold text-purple-800 mb-2">📋 Seu Perfil Olfativo</h2>
        <p className="text-gray-700">{result.perfil_usuario}</p>
      </div>

      {/* Recomendações */}
      <div className="space-y-6">
        {result.recomendacoes.map((perfume, index) => (
          <PerfumeCard key={perfume.nome} perfume={perfume} ranking={index + 1} />
        ))}
      </div>

      {/* Dica extra */}
      {result.dica_extra && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
          <p className="text-yellow-800">
            <span className="font-semibold">💡 Dica:</span> {result.dica_extra}
          </p>
        </div>
      )}

      {/* Botão refazer */}
      <button
        onClick={onRestart}
        className="w-full py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-all"
      >
        🔄 Refazer Quiz
      </button>
    </div>
  );
}

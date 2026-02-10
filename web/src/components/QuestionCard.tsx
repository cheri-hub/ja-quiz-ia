import type { QuizQuestion } from "../types";

interface QuestionCardProps {
  question: QuizQuestion;
  currentAnswer: string | string[] | undefined;
  onAnswer: (questionId: string, value: string | string[]) => void;
}

export function QuestionCard({ question, currentAnswer, onAnswer }: QuestionCardProps) {
  const handleSelectOption = (value: string) => {
    if (question.tipo === "multiselect") {
      const currentValues = (currentAnswer as string[]) || [];
      if (currentValues.includes(value)) {
        onAnswer(question.id, currentValues.filter((v) => v !== value));
      } else {
        onAnswer(question.id, [...currentValues, value]);
      }
    } else {
      onAnswer(question.id, value);
    }
  };

  const isSelected = (value: string) => {
    if (question.tipo === "multiselect") {
      return (currentAnswer as string[])?.includes(value);
    }
    return currentAnswer === value;
  };

  if (question.tipo === "text") {
    return (
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">{question.pergunta}</h2>
          {question.descricao && (
            <p className="text-gray-500 text-sm mt-1">{question.descricao}</p>
          )}
        </div>
        <textarea
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          rows={3}
          placeholder="Digite aqui... (opcional)"
          value={(currentAnswer as string) || ""}
          onChange={(e) => onAnswer(question.id, e.target.value)}
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">{question.pergunta}</h2>
        {question.descricao && (
          <p className="text-gray-500 text-sm mt-1">{question.descricao}</p>
        )}
        {question.tipo === "multiselect" && (
          <p className="text-purple-600 text-sm mt-1">Selecione uma ou mais opções</p>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {question.opcoes?.map((option) => (
          <button
            key={option.valor}
            onClick={() => handleSelectOption(option.valor)}
            className={`p-4 rounded-lg border-2 transition-all text-left hover:shadow-md ${
              isSelected(option.valor)
                ? "border-purple-500 bg-purple-50 shadow-md"
                : "border-gray-200 hover:border-purple-300"
            }`}
          >
            <div className="flex items-center gap-3">
              {option.emoji && <span className="text-2xl">{option.emoji}</span>}
              <div>
                <span className="font-medium text-gray-800">{option.label}</span>
                {option.descricao && (
                  <p className="text-gray-500 text-sm">{option.descricao}</p>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

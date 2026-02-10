import { useState, useEffect } from "react";
import { api } from "../api";
import type { QuizQuestion, QuizAnswers, QuizResult } from "../types";
import { QuestionCard } from "./QuestionCard";
import { ResultsDisplay } from "./ResultsDisplay";

type QuizState = "loading" | "quiz" | "submitting" | "result" | "error";

export function QuizContainer() {
  const [state, setState] = useState<QuizState>("loading");
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setState("loading");
      const data = await api.getQuestions();
      setQuestions(data.perguntas);
      setState("quiz");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar perguntas");
      setState("error");
    }
  };

  const handleAnswer = (questionId: string, value: string | string[]) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  };

  const canProceed = () => {
    const currentQuestion = questions[currentStep];
    if (!currentQuestion.obrigatoria) return true;
    
    const answer = answers[currentQuestion.id];
    if (currentQuestion.tipo === "multiselect") {
      return Array.isArray(answer) && answer.length > 0;
    }
    return !!answer;
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setState("submitting");

      // Construir o objeto de respostas tipado
      const quizAnswers: QuizAnswers = {
        genero: answers.genero as QuizAnswers["genero"],
        ocasiao: answers.ocasiao as QuizAnswers["ocasiao"],
        estacao: answers.estacao as QuizAnswers["estacao"],
        intensidade: answers.intensidade as QuizAnswers["intensidade"],
        familia_olfativa: answers.familia_olfativa as QuizAnswers["familia_olfativa"],
        personalidade: answers.personalidade as QuizAnswers["personalidade"],
        faixa_preco: (answers.faixa_preco as QuizAnswers["faixa_preco"]) || "qualquer",
        notas_preferidas: answers.notas_preferidas as string[],
        notas_evitar: answers.notas_evitar as string[],
        observacoes: answers.observacoes as string,
      };

      const data = await api.submitQuiz(quizAnswers);
      setResult(data);
      setState("result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar quiz");
      setState("error");
    }
  };

  const handleRestart = () => {
    setAnswers({});
    setCurrentStep(0);
    setResult(null);
    setState("quiz");
  };

  // Loading state
  if (state === "loading") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
        <p className="mt-4 text-gray-600">Carregando quiz...</p>
      </div>
    );
  }

  // Error state
  if (state === "error") {
    return (
      <div className="text-center p-8">
        <p className="text-red-500 text-lg mb-4">❌ {error}</p>
        <button
          onClick={loadQuestions}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  // Submitting state
  if (state === "submitting") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
        <p className="mt-4 text-gray-600">Analisando suas preferências com IA...</p>
        <p className="text-sm text-gray-500">Isso pode levar alguns segundos</p>
      </div>
    );
  }

  // Result state
  if (state === "result" && result) {
    return <ResultsDisplay result={result} onRestart={handleRestart} />;
  }

  // Quiz state
  const currentQuestion = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;
  const isLastQuestion = currentStep === questions.length - 1;

  return (
    <div className="space-y-6">
      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Pergunta {currentStep + 1} de {questions.length}</span>
          <span>{Math.round(progress)}% concluído</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <QuestionCard
        question={currentQuestion}
        currentAnswer={answers[currentQuestion.id]}
        onAnswer={handleAnswer}
      />

      {/* Navigation */}
      <div className="flex gap-4">
        <button
          onClick={handlePrev}
          disabled={currentStep === 0}
          className="flex-1 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          ← Anterior
        </button>

        {isLastQuestion ? (
          <button
            onClick={handleSubmit}
            disabled={!canProceed()}
            className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Descobrir Perfumes 🎉
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="flex-1 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Próxima →
          </button>
        )}
      </div>
    </div>
  );
}

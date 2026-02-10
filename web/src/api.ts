import type { QuizAnswers, QuizQuestionsResponse, QuizResult } from "./types";

// Em produção usa /api (nginx proxy), em desenvolvimento usa localhost
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD ? "/api" : "http://localhost:8000");

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Erro ${response.status}`);
    }

    return response.json();
  }

  async getQuestions(): Promise<QuizQuestionsResponse> {
    return this.request<QuizQuestionsResponse>("/quiz/questions");
  }

  async submitQuiz(answers: QuizAnswers): Promise<QuizResult> {
    return this.request<QuizResult>("/quiz/recommend", {
      method: "POST",
      body: JSON.stringify(answers),
    });
  }

  async healthCheck(): Promise<{ status: string; gemini_configured: boolean; perfumes_loaded: number }> {
    return this.request("/health");
  }
}

export const api = new ApiService();

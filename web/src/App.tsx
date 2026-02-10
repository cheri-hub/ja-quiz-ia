import { QuizContainer } from "./components/QuizContainer";

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            JA Essence de la Vie
          </h1>
          <p className="text-gray-500 text-sm">Quiz de Perfumes com IA</p>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl p-6 md:p-8">
          <QuizContainer />
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-500 text-sm">
        Powered by Gemini AI
      </footer>
    </div>
  );
}

export default App;

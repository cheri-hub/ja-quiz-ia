import type { PerfumeRecomendado } from "../types";

interface PerfumeCardProps {
  perfume: PerfumeRecomendado;
  ranking: number;
}

export function PerfumeCard({ perfume, ranking }: PerfumeCardProps) {
  const getMedalColor = () => {
    switch (ranking) {
      case 1:
        return "from-yellow-400 to-amber-500";
      case 2:
        return "from-gray-300 to-gray-400";
      case 3:
        return "from-orange-400 to-orange-600";
      default:
        return "from-purple-400 to-purple-600";
    }
  };

  const getMedalEmoji = () => {
    switch (ranking) {
      case 1:
        return "🥇";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return "🎖️";
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      {/* Header com ranking */}
      <div className={`bg-gradient-to-r ${getMedalColor()} p-3 flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          <span className="text-2xl">{getMedalEmoji()}</span>
          <span className="text-white font-bold text-lg">#{ranking} Match</span>
        </div>
        <div className="bg-white/90 px-3 py-1 rounded-full">
          <span className="font-bold text-gray-800">{perfume.match_score}%</span>
        </div>
      </div>

      <div className="p-5">
        {/* Imagem e info básica */}
        <div className="flex gap-4">
          {perfume.imagem_url ? (
            <img
              src={perfume.imagem_url}
              alt={perfume.nome}
              className="w-24 h-24 object-cover rounded-lg"
            />
          ) : (
            <div className="w-24 h-24 bg-gray-100 rounded-lg flex items-center justify-center">
              <span className="text-4xl">🧴</span>
            </div>
          )}
          <div className="flex-1">
            <h3 className="font-bold text-lg text-gray-800">{perfume.nome}</h3>
            <p className="text-purple-600 text-sm font-medium">{perfume.categoria}</p>
            {perfume.volume && (
              <p className="text-gray-500 text-sm">{perfume.volume}</p>
            )}
            {perfume.inspiracao && (
              <p className="text-gray-600 text-sm mt-1 italic">
                Inspirado em: {perfume.inspiracao}
              </p>
            )}
          </div>
        </div>

        {/* Preço */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              {perfume.preco_pix && (
                <p className="text-green-600 font-bold text-xl">{perfume.preco_pix}</p>
              )}
              {perfume.preco && perfume.preco !== perfume.preco_pix && (
                <p className="text-gray-500 text-sm">ou {perfume.preco}</p>
              )}
              {perfume.parcelamento && (
                <p className="text-gray-500 text-xs">{perfume.parcelamento}</p>
              )}
            </div>
            {perfume.desconto && (
              <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm font-bold">
                {perfume.desconto}
              </span>
            )}
          </div>
        </div>

        {/* Motivo da recomendação */}
        <div className="mt-4 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-500">
          <p className="text-sm text-gray-700">
            <span className="font-semibold text-purple-700">Por que combina com você:</span>
            <br />
            {perfume.motivo_recomendacao}
          </p>
        </div>

        {/* Notas olfativas */}
        {(perfume.notas_topo || perfume.notas_coracao || perfume.notas_fundo) && (
          <div className="mt-4 space-y-2">
            <p className="font-semibold text-gray-700 text-sm">Pirâmide Olfativa:</p>
            {perfume.notas_topo && (
              <p className="text-sm text-gray-600">
                <span className="text-purple-600">🔺 Topo:</span> {perfume.notas_topo}
              </p>
            )}
            {perfume.notas_coracao && (
              <p className="text-sm text-gray-600">
                <span className="text-purple-600">💜 Coração:</span> {perfume.notas_coracao}
              </p>
            )}
            {perfume.notas_fundo && (
              <p className="text-sm text-gray-600">
                <span className="text-purple-600">🔻 Fundo:</span> {perfume.notas_fundo}
              </p>
            )}
          </div>
        )}

        {/* Link produto */}
        {perfume.link_produto && (
          <a
            href={perfume.link_produto}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 block w-full text-center bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all"
          >
            Ver Produto 🛒
          </a>
        )}
      </div>
    </div>
  );
}

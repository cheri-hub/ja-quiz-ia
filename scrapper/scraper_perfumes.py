"""
Scraper de Perfumes - JA Essence de la Vie
==========================================
Script para extrair informações de perfumes das páginas:
- Compartilháveis
- Masculinos
- Femininos

Site: wBuy Platform (sistemawbuy.com.br)
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict
from urllib.parse import urljoin


@dataclass
class Perfume:
    nome: str
    categoria: str
    preco: Optional[str] = None
    preco_original: Optional[str] = None
    preco_pix: Optional[str] = None
    parcelamento: Optional[str] = None
    descricao: Optional[str] = None
    imagem_url: Optional[str] = None
    link_produto: Optional[str] = None
    notas_topo: Optional[str] = None
    notas_coracao: Optional[str] = None
    notas_fundo: Optional[str] = None
    inspiracao: Optional[str] = None
    volume: Optional[str] = None
    desconto: Optional[str] = None
    top_3_comentarios: List[Dict] = field(default_factory=list)


class PerfumeScraper:
    BASE_URL = "https://www.jaessencedelavie.com.br"
    
    # URLs das categorias
    URLS = {
        "compartilhaveis": f"{BASE_URL}/compartilhaveis/",
        "masculinos": f"{BASE_URL}/masculinos/",
        "femininos": f"{BASE_URL}/femininos/"
    }
    
    # API wBuy para paginação (descoberta via análise do site)
    API_URL = f"{BASE_URL}/busca"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.perfumes: List[Perfume] = []
        self.seen_links = set()  # Evitar duplicatas
        self._init_session()
    
    def _init_session(self):
        """Inicializa a sessão visitando a homepage para obter cookies."""
        try:
            print("  Inicializando sessão...")
            self.session.get(self.BASE_URL, timeout=30)
        except:
            pass

    def get_page(self, url: str, retry: int = 3) -> Optional[BeautifulSoup]:
        """Faz requisição e retorna o BeautifulSoup da página."""
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except requests.RequestException as e:
                if attempt < retry - 1:
                    time.sleep(2)
                    continue
                print(f"  ✗ Erro ao acessar {url}: {e}")
                return None
        return None

    def get_page_with_offset(self, category_url: str, offset: int = 0) -> Optional[BeautifulSoup]:
        """Obtém página com offset para paginação via scroll infinito."""
        # wBuy usa AJAX para carregar mais produtos
        url = f"{category_url}?offset={offset}"
        return self.get_page(url)

    def extract_products_from_listing(self, soup: BeautifulSoup, categoria: str) -> List[Perfume]:
        """Extrai produtos da página de listagem wBuy."""
        products = []
        
        # wBuy usa estrutura específica para produtos
        # Procurar por links de produtos e seus containers
        product_links = soup.find_all("a", href=re.compile(r"\.com\.br/[a-z0-9\-]+/$"))
        
        # Extrair blocos de produtos únicos
        processed_urls = set()
        
        # Procurar containers de produtos (estrutura wBuy)
        product_containers = soup.select("div[class*='product'], div[class*='item'], article")
        
        if not product_containers:
            # Fallback: processar links diretamente
            for link in product_links:
                href = link.get("href", "")
                if href and href not in processed_urls:
                    # Verificar se é um link de produto válido (não categoria, não página)
                    if any(x in href for x in ["/compartilhave", "/masculin", "/feminin", 
                                                "/login", "/carrinho", "/politica", "/avaliacoes"]):
                        if href in [self.URLS["compartilhaveis"], self.URLS["masculinos"], self.URLS["femininos"]]:
                            continue
                    
                    nome = link.get_text(strip=True)
                    if nome and len(nome) > 5 and "inspirado" in nome.lower():
                        processed_urls.add(href)
                        
                        perfume = Perfume(
                            nome=nome,
                            categoria=categoria,
                            link_produto=href if href.startswith("http") else urljoin(self.BASE_URL, href)
                        )
                        
                        # Tentar extrair imagem próxima
                        img = link.find("img")
                        if img:
                            perfume.imagem_url = img.get("src") or img.get("data-src")
                        
                        products.append(perfume)
        
        return products

    def extract_price_from_text(self, text: str) -> Dict[str, Optional[str]]:
        """Extrai informações de preço do texto."""
        result = {
            "preco": None,
            "preco_original": None,
            "preco_pix": None,
            "parcelamento": None,
            "desconto": None
        }
        
        # Preço com desconto: "de R$165,90 por R$134,90"
        promo_match = re.search(r"de\s*R\$\s*([\d.,]+)\s*por\s*R\$\s*([\d.,]+)", text)
        if promo_match:
            result["preco_original"] = f"R${promo_match.group(1)}"
            result["preco"] = f"R${promo_match.group(2)}"
        
        # Preço normal: "R$179,90"
        if not result["preco"]:
            price_match = re.search(r"R\$\s*([\d.,]+)", text)
            if price_match:
                result["preco"] = f"R${price_match.group(1)}"
        
        # Preço PIX: "R$170,90 com PIX"
        pix_match = re.search(r"R\$\s*([\d.,]+)\s*com\s*PIX", text)
        if pix_match:
            result["preco_pix"] = f"R${pix_match.group(1)}"
        
        # Parcelamento: "6x de R$29,98"
        parcel_match = re.search(r"(\d+)x\s*de\s*R\$\s*([\d.,]+)", text)
        if parcel_match:
            result["parcelamento"] = f"{parcel_match.group(1)}x de R${parcel_match.group(2)}"
        
        # Desconto: "-19%" ou "(-5%)"
        discount_match = re.search(r"-?\s*(\d+)\s*%", text)
        if discount_match:
            result["desconto"] = f"-{discount_match.group(1)}%"
        
        return result

    def get_product_details(self, perfume: Perfume) -> Perfume:
        """Acessa a página do produto para obter mais detalhes."""
        if not perfume.link_produto:
            return perfume
        
        if perfume.link_produto in self.seen_links:
            return perfume
        self.seen_links.add(perfume.link_produto)
        
        soup = self.get_page(perfume.link_produto)
        if not soup:
            return perfume
        
        # Extrair todo o texto da página para processamento
        page_text = soup.get_text(separator=" ", strip=True)
        
        # ===== PREÇOS =====
        price_info = self.extract_price_from_text(page_text)
        perfume.preco = price_info["preco"]
        perfume.preco_original = price_info["preco_original"]
        perfume.preco_pix = price_info["preco_pix"]
        perfume.parcelamento = price_info["parcelamento"]
        perfume.desconto = price_info["desconto"]
        
        # ===== VOLUME =====
        volume_match = re.search(r"(\d+)\s*ML\b", page_text, re.IGNORECASE)
        if volume_match:
            perfume.volume = f"{volume_match.group(1)}ml"
        
        # ===== INSPIRAÇÃO =====
        # Buscar no título ou texto: "Inspirado em X"
        insp_match = re.search(r"[Ii]nspirado\s+em\s+([^-–\n]+?)(?:\s*[-–]|\s*Compartilhável|\s*Masculino|\s*Feminino|\s*PROMOÇÃO|$)", page_text)
        if insp_match:
            inspiracao = insp_match.group(1).strip()
            # Limpar texto de promoção
            inspiracao = re.sub(r"\s*PROMOÇÃO.*$", "", inspiracao, flags=re.IGNORECASE)
            inspiracao = re.sub(r"\s*Até\s*\d+x.*$", "", inspiracao, flags=re.IGNORECASE)
            perfume.inspiracao = inspiracao.strip()
        
        # ===== NOTAS OLFATIVAS =====
        # Notas de Topo
        topo_match = re.search(r"Notas?\s+de\s+Topo[:\s]+([^N]+?)(?:Notas?\s+de\s+Cora|$)", page_text, re.IGNORECASE)
        if topo_match:
            perfume.notas_topo = topo_match.group(1).strip()
        
        # Notas de Coração
        coracao_match = re.search(r"Notas?\s+de\s+Cora[çc][ãa]o[:\s]+([^N]+?)(?:Notas?\s+de\s+Fundo|$)", page_text, re.IGNORECASE)
        if coracao_match:
            perfume.notas_coracao = coracao_match.group(1).strip()
        
        # Notas de Fundo
        fundo_match = re.search(r"Notas?\s+de\s+Fundo[:\s]+([^\n✦]+)", page_text, re.IGNORECASE)
        if fundo_match:
            perfume.notas_fundo = fundo_match.group(1).strip()
        
        # ===== DESCRIÇÃO =====
        # Procurar texto descritivo na página - "A Experiência" section
        perfume.descricao = None
        
        # Melhor fonte: seção "A Experiência" que descreve a fragrância
        exp_match = re.search(r"A Experiência\s*(.+?)(?:✦|Dicas de Uso|Disclaimer|$)", page_text, re.IGNORECASE | re.DOTALL)
        if exp_match:
            desc = exp_match.group(1).strip()
            desc = re.sub(r"\s+", " ", desc).strip()
            if len(desc) > 20 and len(desc) < 500 and "Ver tudo" not in desc:
                perfume.descricao = desc[:400]
        
        # Fallback: texto após "Inspirado em X"
        if not perfume.descricao:
            desc_match = re.search(r"([OUÉé][\w\s]+(?:fragrância|frescor|elegância|intensidade|sofisticação)[^\n✦]+)", page_text)
            if desc_match:
                desc = desc_match.group(1).strip()
                desc = re.sub(r"\s+", " ", desc).strip()
                if len(desc) > 30 and "Ver tudo" not in desc:
                    perfume.descricao = desc[:400]
        
        # ===== IMAGEM =====
        if not perfume.imagem_url:
            img_elem = soup.select_one("img[src*='produtos']")
            if img_elem:
                perfume.imagem_url = img_elem.get("src") or img_elem.get("data-src")
        
        # ===== TOP 3 COMENTÁRIOS =====
        perfume.top_3_comentarios = self.extract_reviews(soup)
        
        return perfume

    def extract_reviews(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrai os top 3 comentários da página do produto."""
        reviews = []
        
        page_text = soup.get_text()
        
        # Padrão melhorado para wBuy: "DD/MM/YYYY" seguido de texto e "Compra verificada"
        # Os comentários aparecem após a seção "Avaliações"
        
        # Encontrar a seção de avaliações
        avaliacoes_match = re.search(r"Avaliações(.+?)(?:Você também pode gostar|Carregar mais|$)", page_text, re.DOTALL)
        
        if avaliacoes_match:
            avaliacoes_text = avaliacoes_match.group(1)
            
            # Padrão: data + texto + autor + "Compra verificada"
            # Ex: "03/02/2026 Magnífico Katia Martins Compra verificada"
            review_pattern = r"(\d{2}/\d{2}/\d{4})\s*(.+?)(?:Compra verificada|(?=\d{2}/\d{2}/\d{4})|$)"
            matches = re.findall(review_pattern, avaliacoes_text, re.DOTALL)
            
            for date, content in matches[:5]:
                content = content.strip()
                if len(content) < 5 or len(content) > 500:
                    continue
                
                # Tentar separar comentário do autor
                # O autor geralmente é um nome próprio no final
                parts = content.rsplit(' ', 2)
                if len(parts) >= 2:
                    # Verificar se últimas palavras parecem nome
                    potential_author = ' '.join(parts[-2:]) if len(parts) >= 2 else parts[-1]
                    if re.match(r'^[A-Z][a-záàâãéèêíïóôõúüç]+(?:\s+[A-Z][a-záàâãéèêíïóôõúüç]+)*$', potential_author):
                        autor = potential_author
                        comentario = ' '.join(parts[:-2]) if len(parts) > 2 else content
                    else:
                        autor = "Cliente verificado"
                        comentario = content
                else:
                    autor = "Cliente verificado"
                    comentario = content
                
                # Limpar comentário
                comentario = re.sub(r'\s+', ' ', comentario).strip()
                
                if len(comentario) > 3:
                    review = {
                        "data": date,
                        "autor": autor,
                        "comentario": comentario[:300],
                        "verificado": True
                    }
                    reviews.append(review)
        
        return reviews[:3]

    def get_all_products_from_category(self, category_url: str, categoria: str) -> List[Perfume]:
        """Obtém todos os produtos de uma categoria, tratando paginação."""
        all_products = []
        processed_links = set()
        
        # Primeira página
        print(f"  Acessando: {category_url}")
        soup = self.get_page(category_url)
        if not soup:
            return all_products
        
        # Encontrar total de produtos
        total_match = re.search(r"(\d+)\s*itens?", soup.get_text())
        total_products = int(total_match.group(1)) if total_match else 24
        print(f"  Total de itens na categoria: {total_products}")
        
        # Extrair todos os links de produtos da página
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Verificar se parece link de produto (contém "inspirado" ou "perfume")
            if ('inspirado' in text.lower() or 'perfume' in text.lower()) and len(text) > 10:
                # Construir URL completa
                if not href.startswith('http'):
                    full_url = urljoin(self.BASE_URL, href)
                else:
                    full_url = href
                
                # Evitar duplicatas
                if full_url in processed_links:
                    continue
                processed_links.add(full_url)
                
                perfume = Perfume(
                    nome=text,
                    categoria=categoria,
                    link_produto=full_url
                )
                
                # Tentar extrair imagem próxima
                parent = link.find_parent()
                if parent:
                    img = parent.find('img')
                    if img:
                        perfume.imagem_url = img.get('src') or img.get('data-src')
                
                all_products.append(perfume)
        
        print(f"  Produtos encontrados: {len(all_products)}")
        return all_products

    def scrape_category(self, categoria: str, url: str, get_details: bool = True):
        """Faz scraping de uma categoria completa."""
        print(f"\n{'='*60}")
        print(f"📦 Scraping categoria: {categoria.upper()}")
        print(f"{'='*60}")
        
        # Obter todos os produtos
        category_products = self.get_all_products_from_category(url, categoria)
        
        # Obter detalhes de cada produto
        if get_details and category_products:
            print(f"  Obtendo detalhes dos produtos...")
            for i, perfume in enumerate(category_products):
                print(f"    [{i+1}/{len(category_products)}] {perfume.nome[:50]}...")
                self.get_product_details(perfume)
                time.sleep(0.5)  # Delay entre requisições
        
        self.perfumes.extend(category_products)
        print(f"  ✓ {len(category_products)} produtos processados")
        return category_products

    def scrape_all(self, get_details: bool = True):
        """Faz scraping de todas as categorias."""
        print("\n" + "="*60)
        print("🚀 INICIANDO SCRAPING DE PERFUMES - JA ESSENCE DE LA VIE")
        print("="*60)
        
        for categoria, url in self.URLS.items():
            self.scrape_category(categoria, url, get_details)
            time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"✅ TOTAL DE PERFUMES COLETADOS: {len(self.perfumes)}")
        print(f"{'='*60}")
        
        return self.perfumes

    def save_to_json(self, filename: str = "perfumes.json"):
        """Salva os dados em formato JSON."""
        data = [asdict(p) for p in self.perfumes]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Dados salvos em: {filename}")

    def save_to_csv(self, filename: str = "perfumes.csv"):
        """Salva os dados em formato CSV."""
        if not self.perfumes:
            print("Nenhum perfume para salvar.")
            return
        
        # Converter comentários para string
        data = []
        for p in self.perfumes:
            row = asdict(p)
            row["top_3_comentarios"] = json.dumps(row["top_3_comentarios"], ensure_ascii=False)
            data.append(row)
        
        fieldnames = list(data[0].keys())
        
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"💾 Dados salvos em: {filename}")

    def print_summary(self):
        """Imprime um resumo dos dados coletados."""
        print("\n" + "="*60)
        print("📊 RESUMO DOS PERFUMES COLETADOS")
        print("="*60)
        
        categorias = {}
        for p in self.perfumes:
            if p.categoria not in categorias:
                categorias[p.categoria] = []
            categorias[p.categoria].append(p)
        
        for cat, perfumes in categorias.items():
            print(f"\n{cat.upper()} ({len(perfumes)} produtos):")
            print("-"*50)
            for p in perfumes[:5]:  # Mostrar primeiros 5
                preco_str = p.preco_pix or p.preco or "Preço não disponível"
                print(f"  • {p.nome[:50]}")
                print(f"    💰 Preço: {preco_str}")
                if p.inspiracao:
                    print(f"    🎯 Inspirado em: {p.inspiracao[:40]}")
                if p.top_3_comentarios:
                    print(f"    💬 Comentários: {len(p.top_3_comentarios)}")
            if len(perfumes) > 5:
                print(f"  ... e mais {len(perfumes) - 5} produtos")


def main():
    """Função principal."""
    scraper = PerfumeScraper()
    
    try:
        # Fazer scraping de todas as categorias
        # Set get_details=True para obter informações detalhadas de cada produto
        # Set get_details=False para apenas listar os produtos (mais rápido)
        scraper.scrape_all(get_details=True)
        
        # Salvar resultados
        scraper.save_to_json("perfumes.json")
        scraper.save_to_csv("perfumes.csv")
        
        # Mostrar resumo
        scraper.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scraping interrompido pelo usuário.")
        if scraper.perfumes:
            print("Salvando dados coletados até agora...")
            scraper.save_to_json("perfumes_parcial.json")
            scraper.save_to_csv("perfumes_parcial.csv")
    
    except Exception as e:
        print(f"\n❌ Erro durante o scraping: {e}")
        import traceback
        traceback.print_exc()
        if scraper.perfumes:
            print("Salvando dados coletados até agora...")
            scraper.save_to_json("perfumes_erro.json")


if __name__ == "__main__":
    main()

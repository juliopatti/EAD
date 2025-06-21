import requests
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import pandas as pd
from bs4 import BeautifulSoup
import os
import re
import zipfile
from urllib.parse import urljoin
from tqdm import tqdm
from utils import pode_rastrear

# URL base do site e do robots.txt
BASE_URL = "https://portal.inmet.gov.br"
TARGET_PATH = "/dadoshistoricos"
ROBOTS_URL = urljoin(BASE_URL, "/robots.txt")
USER_AGENT = "MeuScraper/1.0 (mailto:julio.patti@gmail.com)"


def salva_html(url: str) -> str:
    """
    Baixa o HTML da página se permitido. Lança exceção em caso de bloqueio ou erro HTTP.
    """
    if not pode_rastrear(url, user_agent=USER_AGENT, robots_url=ROBOTS_URL):
        raise RuntimeError(f"Bloqueado pelo robots.txt: {url}")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        time.sleep(2)
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erro HTTP ao baixar {url}: {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Falha de conexão ao acessar {url}: {e}") from e
    
    # Salva em arquivo local
    arquivo_saida = "data/meteorologicos.html"
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML salvo em {arquivo_saida}")
    return html


def get_dataframe(html: str) -> pd.DataFrame:
    """
    Recebe o HTML da página de dados históricos e retorna um DataFrame com as colunas:
      - ANO_AUTOMATICA: texto do link (ex: "ANO 2000 (AUTOMÁTICA)")
      - link: URL completa para o .zip
    """
    soup = BeautifulSoup(html, "html.parser")
    registros = []
    for artigo in soup.select("article.post-preview"):
        a = artigo.find("a")
        if a and a.get("href"):
            registros.append({
                "ANO_AUTOMATICA": a.get_text(strip=True),
                "link": a["href"]
            })
    df = pd.DataFrame(registros)
    df['ANO_AUTOMATICA'] = df['ANO_AUTOMATICA'].str.split().str[1]
    df = df[df['link'].astype(str).str.lower().str.split('.').str[-1] == 'zip']
    return df.reset_index(drop=True)


def download_and_unzip(
    link: str,
    base_url: str = BASE_URL,
    user_agent: str = USER_AGENT,
    output_folder: str = "data/meteorologia"
) -> None:
    """
    Baixa um arquivo ZIP da URL (relativa ou absoluta) e extrai seu conteúdo
    em `output_folder`.

    Parâmetros:
    - link: URL ou path relativo para o .zip
    - base_url: URL base para resolver links relativos
    - user_agent: string usada no header de requisição
    - output_folder: diretório onde o ZIP será salvo, extraído e deletado após extração.
    """
    # Garante que o diretório existe
    os.makedirs(output_folder, exist_ok=True)

    # Resolve URL completa
    zip_url = link if link.startswith(("http://", "https://")) else urljoin(base_url, link)
    
    # Verifica permissão pelo robots.txt
    if not pode_rastrear(zip_url, user_agent=USER_AGENT, robots_url=ROBOTS_URL):
        raise RuntimeError(f"Bloqueado pelo robots.txt: {zip_url}")

    # Define caminho local para salvar o ZIP
    local_zip = os.path.join(output_folder, os.path.basename(zip_url))

    # Faz download do ZIP, em modo stream
    headers = {"User-Agent": user_agent}
    try:
        time.sleep(11)  # atraso gentil
        resp = requests.get(zip_url, headers=headers, timeout=20, stream=True)
        resp.raise_for_status()
        with open(local_zip, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"Erro HTTP ao baixar {zip_url}: {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Falha de conexão ao baixar {zip_url}: {e}") from e

    # Extrai o ZIP
    try:
        with zipfile.ZipFile(local_zip, "r") as z:
            z.extractall(output_folder)
    except zipfile.BadZipFile as e:
        raise RuntimeError(f"Arquivo ZIP inválido ou corrompido: {local_zip}: {e}") from e
    
    # Remove o arquivo ZIP baixado
    try:
        os.remove(local_zip)
    except OSError as e:
        print(f"Aviso: não foi possível remover {local_zip}: {e}")

    # print(f"Download e extração concluídos em: {output_folder}")


def main():
    full_url = urljoin(BASE_URL, TARGET_PATH)
    print(f"Verificando permissão e baixando: {full_url}")

    html = salva_html(full_url)
    df_links = get_dataframe(html)
    for link in tqdm(df_links['link'], desc="Baixando arquivos ZIP"):
        try:
            download_and_unzip(link, base_url=BASE_URL, user_agent=USER_AGENT)
        except RuntimeError as e:
            print(f"Erro ao processar {link}: {e}")
        except Exception as e:
            print(f"Erro inesperado ao processar {link}: {e}")
            
    print(f'Extração de {df_links.shape[0]} ZIPs terminada')
    
if __name__ == "__main__":
    main()
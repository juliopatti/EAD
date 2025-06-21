import os
import time
import pandas as pd
import requests
from tqdm import tqdm
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathlib import PurePosixPath
from utils import pode_rastrear

# --- CONFIGURAÇÕES ---
BASE_URL = "https://dados.antt.gov.br/dataset"
SEARCH_URL = (
    f"{BASE_URL}"
    "/acidentes-rodovias"
)
HTML_PATH = "data/acidentes.html"
DOWNLOAD_DIR = "data/acidentes"
ROBOTS_URL = urljoin(BASE_URL, "/robots.txt")
USER_AGENT  = "MeuScraper/1.0 (mailto:julio.patti@gmail.com)"
# ----------------------

def salva_html(search_url: str, html_path: str) -> None:
    """Abre a página com Playwright, salva o HTML localmente."""
    
    # verifica permissão de acesso à página
    if not pode_rastrear(search_url, user_agent=USER_AGENT, robots_url=ROBOTS_URL):
        raise RuntimeError(f"Bloqueado pelo robots.txt: {search_url}")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()
        
        time.sleep(11)
        page.goto(search_url, timeout=60000)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Salvando HTML de: {search_url} → {html_path}")

def get_dataframe(html_path: str) -> pd.DataFrame:
    """Lê o HTML salvo e extrai URLs de CSV num DataFrame."""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    selector = "section#dataset-resources ul.resource-list li.resource-item"
    urls, exts = [], []

    for li in soup.select(selector):
        a = li.select_one("a.resource-url-analytics")
        if not a:
            continue

        url = a["href"].strip()
        ext = PurePosixPath(urlparse(url).path).suffix.lstrip(".").lower()
        if ext == "csv":
            urls.append(url)
            exts.append(ext)

    df = pd.DataFrame({"url": urls, "ext": exts})
    print(f"Encontrados {len(df)} arquivos CSV")
    return df.reset_index(drop=True)

def download_csvs(df: pd.DataFrame, download_dir: str) -> None:
    """Baixa cada CSV do DataFrame para a pasta especificada."""
    os.makedirs(download_dir, exist_ok=True)
    errors = 0

    for url in tqdm(df["url"], desc="Baixando CSVs"):
        
        # checa permissão de download de cada CSV
        if not pode_rastrear(url, user_agent=USER_AGENT, robots_url=ROBOTS_URL):
            raise RuntimeError(f"Bloqueado pelo robots.txt: {url}")
        
        filename = PurePosixPath(urlparse(url).path).name
        dest = os.path.join(download_dir, filename)

        # print(f"Baixando {filename} …", end=" ")
        time.sleep(11)
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT}, 
                timeout=60
            )
            
            resp.raise_for_status()
            with open(dest, "wb") as f:
                f.write(resp.content)
            # print("ok")
        except Exception as e:
            print(f"erro: {e}")
            errors += 1

    print(f"Download de {len(df)} arquivos finalizado ({errors} erros)")

def main():
    salva_html(SEARCH_URL, HTML_PATH)
    df_links = get_dataframe(HTML_PATH)
    download_csvs(df_links, DOWNLOAD_DIR)
    print("Extração de dados de acidentes concluída!")

if __name__ == "__main__":
    main()

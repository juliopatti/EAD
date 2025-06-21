import os
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote, urljoin
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from utils import pode_rastrear

# --- CONFIGURAÇÃO ---
BASE_URL    = "https://servicos.dnit.gov.br"
DNIT_URL    = (
    f"{BASE_URL}/dnitcloud/index.php/"
    "s/oTpPRmYs5AAdiNr?path=%2FSNV%20Bases%20Geom%C3%A9tricas%20(2013-Atual)%20(SHP)"
)
HTML_PATH   = "data/geo_rod.html"
DOWNLOAD_DIR = "data/geoloc"
ROBOTS_URL = urljoin(BASE_URL, "/robots.txt")
USER_AGENT   = "MeuScraper/1.0 (mailto:julio.patti@gmail.com)"
# ----------------------

def main():
    # verifica permissão de scraping da página inicial
    if not pode_rastrear(DNIT_URL, user_agent=USER_AGENT, robots_url=ROBOTS_URL):   # ← novo
        raise RuntimeError(f"Bloqueado pelo robots.txt: {DNIT_URL}")     
    
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    # abre a página e faz scroll dinâmico
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page() 
        page.goto(DNIT_URL, timeout=120_000)
        page.wait_for_load_state("networkidle")

        previous_count = stable_iterations = 0
        while stable_iterations < 2:
            rows = page.locator("tr[data-type='file']")
            count = rows.count()
            if count:
                rows.nth(count - 1).scroll_into_view_if_needed()
            page.wait_for_timeout(3000)

            new_count = page.locator("tr[data-type='file']").count()
            if new_count == previous_count:
                stable_iterations += 1
            else:
                stable_iterations = 0
            previous_count = new_count

        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()

    # salva o HTML
    Path(HTML_PATH).write_text(html, encoding="utf-8")
    print(f"HTML salvo em {HTML_PATH}")

    # lista os nomes de todos os ZIPs encontrados
    soup = BeautifulSoup(html, "html.parser")
    zip_files = [
        s.select_one("span.innernametext").text + s.select_one("span.extension").text
        for s in soup.select("span.nametext")
        if s.select_one("span.extension") and s.select_one("span.extension").text.lower().endswith(".zip")
    ]
    print("Arquivos ZIP encontrados:")
    for fn in zip_files:
        print(" -", fn)
    print("Total:", len(zip_files))

    # monta DataFrame com filename, size, modified e link
    data = []
    for tr in soup.select("tr[data-type='file']"):
        fn = tr["data-file"]
        if not fn.lower().endswith(".zip"):
            continue
        size = tr.select_one("td.filesize").get_text(strip=True)
        modified = tr.select_one("span.modified").get_text(strip=True)
        link = BASE_URL + tr.select_one("a.name")["href"]
        data.append({
            "filename": fn,
            "size": size,
            "modified": modified,
            "link": link
        })

    df = pd.DataFrame(data)
    df = df[df['filename'].str.lower().str.endswith('.zip')]
    df["year"]    = df["filename"].str[:4].astype(int)
    df["month"]   = df["filename"].str[4:6].astype(int)
    df["version"] = df["filename"].str[6]
    df = df.sort_values(
        by=["year", "month", "version"],
        ascending=False
    ).reset_index(drop=True)

    latest      = df.iloc[0]
    latest_name = latest["filename"]
    latest_link = latest["link"]
    print(f"Último ZIP selecionado: {latest_name}")

    # reconstrói a URL direta de download
    parsed     = urlparse(latest_link)
    folder_path = parse_qs(parsed.query)["path"][0]
    full_path   = f"{folder_path}/{latest_name}"
    encoded     = quote(full_path, safe="/")
    download_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?path={encoded}"
    print("Download URL:", download_url)
    
    # verifica permissão de download do ZIP
    if not pode_rastrear(download_url, user_agent=USER_AGENT, robots_url=ROBOTS_URL):  
        raise RuntimeError(f"Bloqueado pelo robots.txt: {download_url}")   

    # baixa e salva o arquivo
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    dest = Path(DOWNLOAD_DIR) / latest_name
    print("Aguardando 10 segundos antes do download…")
    
    # Boas Práticas
    time.sleep(11)
    resp = requests.get(
        download_url,
        headers={"User-Agent": USER_AGENT},
        stream=True,
        timeout=60
    )
    
    resp.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(8192):
            if chunk:
                f.write(chunk)
    print(f"Arquivo salvo como: {dest}")

if __name__ == "__main__":
    main()

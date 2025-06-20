import os
import time
import pandas as pd
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import PurePosixPath

# URL de busca acidentes
search_url = (
    "https://dados.antt.gov.br/dataset"
    "/acidentes-rodovias"
)

os.makedirs("data", exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page    = browser.new_page()
    
    time.sleep(11)
    page.goto(search_url, timeout=60000)
    page.wait_for_load_state("networkidle")
    html = page.content()

    # Salva em data/acidentes.html
    html_path = "data/acidentes.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML de acidentes salvo em {html_path}\n")
    browser.close()


# Lê o HTML
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Seletor CSS que pega cada <li class="resource-item">
selector = "section#dataset-resources ul.resource-list li.resource-item"

urls, exts= [], []
for li in soup.select(selector):
    
    # Título vem no atributo title do <a class="heading">
    heading = li.select_one("a.heading")
    title   = heading["title"].strip()
    print(f"{title}")
    a = li.select_one("a.resource-url-analytics")
    if not a:
        print('not a')
        continue
    url = a["href"].strip()
    ext = PurePosixPath(url).suffix.lstrip(".").lower()
    if ext=="csv":
        urls.append(url), exts.append(url.split(".")[-1])

df_acidentes = pd.DataFrame({"url": urls, "ext": exts})
df_acidentes = df_acidentes.reset_index(drop=True)

download_dir = os.path.join("data", "acidentes")
os.makedirs(download_dir, exist_ok=True)

urls = df_acidentes['url'].tolist()
for url in urls:
    path = urlparse(url).path
    filename = PurePosixPath(path).name
    dest = os.path.join(download_dir, filename)
    
    print(f"Baixando {filename} …", end=" ")
    time.sleep(11) 
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(resp.content)
        print("ok")
    except Exception as e:
        print("erro:", e)
        
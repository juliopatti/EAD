
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote

dnit_url = (
    "https://servicos.dnit.gov.br/dnitcloud/index.php/"
    "s/oTpPRmYs5AAdiNr?path=%2FSNV%20Bases%20Geom%C3%A9tricas%20(2013-Atual)%20(SHP)"
)
os.makedirs("data", exist_ok=True)

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(dnit_url, timeout=120000)
    page.wait_for_load_state("networkidle")

    previous_count = 0
    stable_iterations = 0

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

soup = BeautifulSoup(html, "html.parser")
zip_files = [
    f"{s.select_one('span.innernametext').text}{s.select_one('span.extension').text}"
    for s in soup.select("span.nametext")
    if s.select_one("span.extension") and s.select_one("span.extension").text.lower().endswith(".zip")
]

print("Arquivos ZIP encontrados:")
for fn in zip_files:
    print(" -", fn)
print("Total:", len(zip_files))

html_path = "data/geo_rod.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
    
# Carrega o HTML salvo
html_path = Path("data/geo_rod.html")
soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
base_url = "https://servicos.dnit.gov.br"

# Extrai todas as linhas de arquivos
rows = soup.select('tr[data-type="file"]')
data = []
for tr in rows:
    data.append({
        "filename": tr["data-file"],                                    
        "size":     tr.select_one("td.filesize").get_text(strip=True),  
        "modified": tr.select_one("span.modified").get_text(strip=True), 
        "link":     base_url + tr.select_one("a.name")["href"]          
    })

# Monta DataFrame, filtra só ZIPs e ordena
df = pd.DataFrame(data)
df = df[df['filename'].str.lower().str.endswith('.zip')]
df['year']    = df['filename'].str[:4].astype(int)
df['month']   = df['filename'].str[4:6].astype(int)
df['version'] = df['filename'].str[6]
df = df.sort_values(by=['year', 'month', 'version'], ascending=False).reset_index(drop=True)

latest      = df.iloc[0]
latest_name = latest['filename']  
latest_link = latest['link']      
parsed      = urlparse(latest_link)
share_id    = parsed.path.split("/s/")[1].split("/")[0]
folder_path = parse_qs(parsed.query)["path"][0]  # ex: "/SNV Bases Geométricas (2013-Atual) (SHP)"
full_path   = f"{folder_path}/{latest_name}"
encoded     = quote(full_path, safe='/')
download_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?path={encoded}"

print("Download URL:", download_url)

# 7) Baixa e salva o arquivo
output_dir = Path("data", "geoloc")
output_dir.mkdir(parents=True, exist_ok=True)
file_path = output_dir / latest_name

print(f'Boas práticas: aguardando 10 sec para requisição de download.')
time.sleep(11) 
resp = requests.get(download_url, stream=True)
resp.raise_for_status()
with open(file_path, "wb") as f:
    for chunk in resp.iter_content(8192):
        if chunk:
            f.write(chunk)

print(f"Arquivo salvo como: {file_path}")

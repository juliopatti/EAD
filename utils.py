from urllib.robotparser import RobotFileParser
import os
import shutil
import re
import pandas as pd

def pode_rastrear(url: str, user_agent: str, robots_url: str) -> bool:
    """
    Verifica no robots.txt se o user-agent tem permissão para acessar a URL dada.
    """
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, url)


def organize_csvs_by_year(base_dir: str = "data/meteorologia") -> pd.DataFrame:
    """
    1) Lista todos os CSVs diretamente em base_dir.
    2) Extrai o ano com regex, buscando (\d{4})\.csv no final do nome.
    3) Monta DataFrame com filepath, filename e year.
    4) Move cada CSV para base_dir/<year>/.
    Retorna o DataFrame antes da movimentação.
    """
    # 1) Listagem de CSVs soltos em base_dir
    all_files = [
        os.path.join(base_dir, fname)
        for fname in os.listdir(base_dir)
        if fname.lower().endswith(".csv")
           and os.path.isfile(os.path.join(base_dir, fname))
    ]

    # 2) DataFrame inicial
    df = pd.DataFrame({"filepath": all_files})
    df["filename"] = df["filepath"].map(os.path.basename)

    # 3) Extrai o 'year' via regex no final do filename
    df["year"] = df["filename"].str.extract(r"(\d{4})\.csv$", flags=re.IGNORECASE)[0]

    # 4) Move cada arquivo para a pasta do ano correspondente
    for yr in df["year"].dropna().unique():
        target_dir = os.path.join(base_dir, yr)
        os.makedirs(target_dir, exist_ok=True)
        subset = df[df["year"] == yr]
        for src in subset["filepath"]:
            dest = os.path.join(target_dir, os.path.basename(src))
            # print(f"Movendo {src} → {dest}")
            shutil.move(src, dest)

    return df



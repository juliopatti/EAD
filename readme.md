# Extração de Dados Públicos de Transporte, Geográficos e Clima no Brasil

Este projeto realiza **extração de dados públicos** das seguintes plataformas governamentais brasileiras:

- [INMET - Instituto Nacional de Meteorologia](https://portal.inmet.gov.br/dadoshistoricos)
- [DNIT - Departamento Nacional de Infraestrutura de Transportes](https://servicos.dnit.gov.br)
- [ANTT - Agência Nacional de Transportes Terrestres](https://dados.antt.gov.br)

## 🚀 Execução

O script principal para **extração bruta (mais de 10 mil arquivos)** é:

```bash
python raw_extraction.py
```

⚠️ Este processo pode levar tempo significativo e exige conexão estável à internet.

---

## 🔧 Configuração do Ambiente

1. **Crie o ambiente virtual:**

```bash
python -m venv venv
```

2. **Ative o ambiente:**

- Windows:
  ```bash
  .\venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Instale os navegadores do Playwright:**

```bash
python -m playwright install
```

---

## 💡 Observações

- Ajustes regionais ou de intervalo de datas podem ser realizados diretamente no script `raw_extraction.py`.
- Para aceleração ou paralelização da execução, considere o uso de bibliotecas como `concurrent.futures` ou `multiprocessing`.

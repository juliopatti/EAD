# Extração de Dados Públicos de Transporte, Geográficos e Clima no Brasil

Este projeto realiza **extração de dados públicos** das seguintes plataformas governamentais brasileiras:

- [INMET - Instituto Nacional de Meteorologia](https://portal.inmet.gov.br/dadoshistoricos)
- [DNIT - Departamento Nacional de Infraestrutura de Transportes](https://servicos.dnit.gov.br)
- [ANTT - Agência Nacional de Transportes Terrestres](https://dados.antt.gov.br)

---

## 🔒 Boas Práticas e Licenças

Na extração dos dados, **respeitamos o arquivo `robots.txt`** de cada plataforma, garantindo a conformidade com suas políticas de acesso. Para evitar sobrecarga nos servidores, cada solicitação é seguida por um **intervalo de espera significativo (geralmente superior a 8 segundos)** antes da próxima.

Os dados brutos extraídos e os dados processados resultantes deste estudo estão disponíveis sob licenças **Creative Commons (CC)**, conforme especificado pelas fontes originais.

---

## 🚀 Execução

O script principal para **extração bruta (mais de 10 mil arquivos)** é:

python raw_extraction.py

⚠️ Este processo pode levar tempo significativo e exige conexão estável à internet.

---

## 🔧 Configuração do Ambiente

1.  **Crie o ambiente virtual:**

    python -m venv venv

2.  **Ative o ambiente:**

    -   Windows:
        .\venv\Scripts\activate
    -   Linux/Mac:
        source venv/bin/activate

3.  **Instale as dependências:**

    pip install -r requirements.txt

4.  **Instale os navegadores do Playwright:**

    python -m playwright install

    ⚠️ **Para usuários Linux:** pode ser necessário instalar a seguinte dependência do sistema:

    sudo apt-get install libavif16

---

## 📊 Dados do Estudo

Os dados extraídos (brutos) e os dados úteis (lapidados e processados) deste estudo estão disponíveis para download e consulta na seguinte pasta do Google Drive:

[Link para a pasta dos dados no Google Drive](https://drive.google.com/drive/folders/12FpgD2oiYrZAPZtlcBomZLEG6OGTC-PK?usp=sharing)
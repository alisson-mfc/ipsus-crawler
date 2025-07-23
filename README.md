Este projeto contém um script de web scraping (crawler) desenvolvido em Python para automatizar o download de documentos de planejamento do Sistema Único de Saúde (SUS) a partir do portal DigiSUS Gestor/Módulos de Planejamento.

O script navega pela plataforma, seleciona estados, municípios e períodos específicos para baixar sistematicamente os seguintes instrumentos:

Plano de Saúde (PS)

Programação Anual de Saúde (PAS)

Relatório Anual de Gestão (RAG)

Os arquivos são salvos localmente em uma estrutura de pastas organizada, facilitando a consulta e a análise de dados em larga escala.

Funcionalidades
Extração Abrangente: Baixa documentos tanto da esfera Estadual quanto Municipal.

Navegação Automatizada: Utiliza Selenium para interagir com os menus e filtros da página, simulando a ação de um usuário.

Estrutura de Pastas Lógica: Organiza os arquivos baixados no seguinte formato:

Documentos_Saude_Brasil/
└── NOME_DO_ESTADO/
    ├── Estadual/
    │   └── TIPO_DE_DOCUMENTO/
    │       └── ANO.pdf
    └── Municipal/
        └── NOME_DO_MUNICIPIO/
            └── TIPO_DE_DOCUMENTO/
                └── ANO.pdf
Configuração Flexível: Permite ajustar facilmente os anos e os períodos de planejamento a serem capturados diretamente no código.

Modo Headless: Pode ser executado em segundo plano, sem abrir uma janela de navegador, ideal para automação em servidores.

Resiliência: Possui mecanismos para aguardar o carregamento de elementos dinâmicos da página e para tratar instabilidades na seleção de municípios.

Pré-requisitos
Antes de executar o script, garanta que você tenha:

Python 3.8 ou superior instalado.

Navegador Google Chrome instalado em seu sistema.

Instalação
Clone ou baixe este repositório:
Se tiver Git, use o comando:

Bash

git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
Caso contrário, apenas baixe o arquivo crawler_digisus.py.

Crie um ambiente virtual (recomendado):

Bash

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
Instale as dependências necessárias:

Bash

pip install requests selenium webdriver-manager
Como Usar
Com o ambiente configurado e as dependências instaladas, basta executar o script no seu terminal:

Bash

python crawler_digisus.py
O script iniciará o processo de navegação e download. O progresso será exibido no terminal, informando qual estado, município e documento está sendo baixado. Ao final, será exibido um resumo do total de arquivos obtidos.

Configuração
É possível personalizar o comportamento do crawler editando as constantes no início do arquivo crawler_digisus.py:

DEST_DIR: Altere o nome da pasta principal onde os documentos serão salvos.

Python

DEST_DIR  = Path("Documentos_Saude_Brasil")
HEADLESS: Defina como False se quiser ver o navegador em ação durante a execução.

Python

HEADLESS  = True # True para rodar em segundo plano, False para ver o navegador
YEARS_MUN e YEARS_EST: Configure os anos de referência que você deseja baixar para cada tipo de documento e esfera de gestão.

Python

# Exemplo para documentos municipais
YEARS_MUN = {
    "Plano de Saúde":               {"2022"}, # Baixar apenas o plano de 2022
    "Programação Anual de Saúde":   {str(y) for y in range(2023, 2025)}, # Baixar PAS de 2023 e 2024
    "Relatório Anual de Gestão":    {str(y) for y in range(2020, 2023)}, # Baixar RAG de 2020 a 2022
    "RAG":                          {str(y) for y in range(2020, 2023)},
}
Aviso Legal
Este script foi criado para fins de pesquisa e automação de coleta de dados públicos. Utilize-o de forma responsável.

Web crawlers são dependentes da estrutura do site-alvo. Mudanças no layout ou na tecnologia do portal DigiSUS podem fazer com que o script pare de funcionar. Se isso ocorrer, será necessário revisar e atualizar os seletores e a lógica de navegação.

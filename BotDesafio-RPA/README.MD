Descrição
Este projeto implementa um robô de automação web (RPA) para coletar dados de beneficiários de programas sociais no Portal da Transparência do Governo Federal. O robô utiliza Selenium WebDriver para navegação e interação com a página web.

Funcionalidades
-Acessa o Portal da Transparência
-Realiza buscas por pessoas físicas
-Aplica filtro de "Beneficiário de Programa Social"
-Captura screenshots dos resultados
-Converte imagens para Base64
-Gera relatório em JSON com os dados coletados

Pré-requisitos
-Python 3.8+
-Google Chrome ou Firefox instalado
-ChromeDriver (compatível com sua versão do Chrome)
-Bibliotecas Python listadas em requirements.txt

Instalação
1.Clone o repositório:


Instale as dependências
2.pip install -r requirements.txt

Configuração

1.Crie um arquivo src/entrada_busca.json com os dados de busca:

Exemplo
{
  "pessoas": [
    {"nome": "Maria Silva", "cpf": "123.456.789-00", "nis": "12345678901"},
    {"nome": "João Santos", "cpf": "987.654.321-00", "nis": "98765432109"}
  ]
}

2.Configure as opções de execução no método __init__ da classe PortalTransparenciaBot:

def __init__(self, headless=False):
    self.options = Options()
    self.options.add_argument("--window-size=1920,1080")
    if headless:
        self.options.add_argument("--headless")

Uso
Execute o robô com o seguinte comando:

python main.py

Outputs

O robô gera:
-Screenshots em data/screenshots/ (ex: pessoa_1.png)
-Arquivo JSON consolidado em data/resultado_final.json

Fluxo do Processo

1.Acessa diretamente a página de busca
2.Aplica filtro de beneficiário social
3.Para cada pessoa no arquivo de entrada:
4.Realiza a busca pelo nome
5.Captura screenshot do resultado
6.Converte imagem para Base64
7.Armazena os dados

Tratamento de Erros
O robô trata:
-Elementos não encontrados
-Timeouts de carregamento
-Ausência de resultados
-Falhas durante o processamento

Melhorias Futuras
-Adicionar suporte a execução paralela
-Implementar sistema de logging
-Adicionar tratamento para CAPTCHAs na área de obtenção de dados de recebimentos de recursos (há um captcha que não foi possível ultrapassar)
-Criar interface de configuração
-Integrar um sistema de banco SQL para armazenamento dos dados coletados


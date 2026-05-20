Retail Sales Analytics Dashboard
📌 Sobre o Projeto

Projeto completo de análise de vendas desenvolvido com foco em Business Intelligence, Engenharia de Dados e análise estratégica de negócio.

O objetivo do projeto foi construir um pipeline de dados completo, desde a extração e tratamento dos dados até a criação de dashboards executivos voltados para tomada de decisão.

O projeto simula um ambiente corporativo real utilizando dados de vendas do varejo para identificar:

oportunidades de crescimento
problemas financeiros
comportamento de clientes
performance de produtos
rentabilidade por segmento e região
🚀 Tecnologias Utilizadas
🐍 Python

Utilizado para desenvolvimento do processo ETL:

Extração dos dados CSV
Tratamento e limpeza
Conversão de datas
Padronização de colunas
Criação de métricas
Automação do carregamento

Bibliotecas utilizadas:

pandas
sqlalchemy
pymysql
🗄️ MySQL

Banco de dados utilizado para:

armazenamento estruturado
modelagem relacional
consultas SQL
integração com Power BI
📊 Power BI

Responsável pela criação dos dashboards analíticos e executivos.

Recursos utilizados:

DAX
modelagem de dados
KPIs
storytelling executivo
análises financeiras
segmentação de clientes
⚙️ Pipeline ETL

O pipeline ETL foi desenvolvido em Python seguindo as etapas:

1. Extração

Leitura do dataset CSV contendo informações de vendas.

2. Transformação

Processo de tratamento dos dados:

renomeação de colunas
conversão de tipos
tratamento de datas
criação de métricas auxiliares
padronização estrutural
3. Carga

Envio automatizado dos dados tratados para o MySQL.

🧱 Estrutura do Projeto
retail-sales-analytics/
│
├── data/
│   └── Superstore.csv
│
├── python/
│   ├── etl_vendas.py
│   └── config.py
│
├── sql/
│   ├── create_tables.sql
│   └── consultas.sql
│
├── powerbi/
│   └── dashboard_vendas.pbix
│
├── images/
│   ├── resumo_executivo.png
│   ├── financeiro.png
│   ├── clientes.png
│   └── desempenho.png
│
├── requirements.txt
└── README.md
📈 Estrutura do Dashboard

O dashboard foi dividido em páginas estratégicas para facilitar a análise executiva e operacional.

🧠 1. Resumo Executivo

Visão estratégica da empresa contendo:

receita total
lucro total
margem operacional
crescimento
principais problemas
oportunidades de negócio
recomendações executivas
📊 2. Visão Geral

Análise macro da operação:

evolução das vendas
evolução do lucro
vendas por categoria
vendas por região
top produtos
🚀 3. Análise de Desempenho

Foco em performance operacional:

lucratividade
margem por categoria
produtos problemáticos
análise comparativa
oportunidades de crescimento
👥 4. Clientes

Análise comportamental da base de clientes:

top clientes
recorrência
ticket médio
segmentação
retenção
oportunidades comerciais
💰 5. Financeiro

Análise financeira estratégica:

margem operacional
produtos com prejuízo
rentabilidade
análise regional
oportunidades financeiras
📌 Principais KPIs

KPIs desenvolvidos no Power BI utilizando DAX:

Receita Total
Lucro Total
Margem %
Ticket Médio
Total Pedidos
Clientes Ativos
Crescimento %
🔍 Principais Insights Encontrados

Durante a análise dos dados foram identificados diversos insights estratégicos:

categorias com alta receita e baixa margem
produtos operando com prejuízo
segmentos mais rentáveis
regiões com oportunidade de expansão
concentração de receita em clientes específicos
💼 Recomendações Estratégicas

Com base nas análises realizadas:

✅ Revisar precificação

Produtos com lucro negativo indicam necessidade de revisão de custos e descontos.

✅ Expandir segmento mais rentável

Segmentos com maior margem operacional representam oportunidade de crescimento.

✅ Estratégia de retenção

Clientes estratégicos devem receber ações de fidelização e relacionamento.

✅ Revisão logística

Categorias com baixa margem podem estar sofrendo impacto operacional.

📊 Dashboard
Resumo Executivo
Adicionar imagem aqui:
images/resumo_executivo.png
Financeiro
Adicionar imagem aqui:
images/financeiro.png
Clientes
Adicionar imagem aqui:
images/clientes.png
🎯 Objetivos do Projeto

Este projeto teve como objetivo praticar e consolidar conhecimentos em:

Python para dados
ETL
SQL
MySQL
Power BI
DAX
Business Intelligence
análise estratégica
storytelling com dados
📌 Conclusão

O projeto foi desenvolvido simulando um cenário corporativo real, buscando transformar dados em informação estratégica para suporte à tomada de decisão.

Além do desenvolvimento técnico, o foco também foi construir análises orientadas ao negócio, aproximando tecnologia e estratégia empresarial.

👨‍💻 Autor

Matheus Marinho

Projeto desenvolvido para fins de estudo, portfólio e evolução profissional na área de Dados e Business Intelligence.

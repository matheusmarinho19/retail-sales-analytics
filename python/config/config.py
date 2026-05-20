# config/config.py
# Configurações centralizadas do projeto

import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / 'src'
LOGS_DIR = BASE_DIR / 'logs'
REPORTS_DIR = BASE_DIR / 'reports'
DATA_DIR = BASE_DIR / 'data'

# Configurações do banco de dados
DB_CONFIG = {
    'usuario': 'root',
    'senha': 'Limites1007@',
    'host': '127.0.0.1',
    'porta': 3306,
    'banco': 'empresa_analitica'
}

# Configurações do ETL
ETL_CONFIG = {
    'caminho_arquivo': "C:/Users/Eliane/Downloads/Arquivos Facul/Analise_Chamados/Vendasteste/Superstore.csv",
    'log_dir': LOGS_DIR / 'etl',
    'backup_dir': BASE_DIR / 'backup'
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Função para garantir que as pastas existem
def ensure_directories():
    """Garante que todas as pastas necessárias existem"""
    directories = [
        LOGS_DIR / 'etl',
        LOGS_DIR / 'analise',
        REPORTS_DIR / 'html',
        REPORTS_DIR / 'excel',
        REPORTS_DIR / 'csv',
        DATA_DIR,
        BASE_DIR / 'backup'
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
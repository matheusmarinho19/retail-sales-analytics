# ============================================
# etl_pipeline.py - Pipeline ETL Automatizado
# ============================================
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import logging
from datetime import datetime
import os
import sys

# Criar pasta de logs se não existir
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    print(f"Pasta '{LOG_DIR}' criada")

# Configurar logging (salvando na pasta logs)
log_filename = os.path.join(LOG_DIR, f'etl_log_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Pipeline ETL automatizado para dados de vendas"""
    
    def __init__(self, config):
        self.config = config
        self.conexao = None
        self.df = None
        self.modelo = {}
        
    def criar_conexao(self):
        """Cria conexão com MySQL"""
        try:
            from urllib.parse import quote_plus
            url_senha = quote_plus(self.config['senha'])
            self.conexao = create_engine(
                f"mysql+pymysql://{self.config['usuario']}:{url_senha}@{self.config['host']}:{self.config['porta']}/{self.config['banco']}",
                pool_pre_ping=True
            )
            logger.info("OK - Conexao com MySQL estabelecida")
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha na conexao: {e}")
            return False
    
    def carregar_dados(self):
        """Carrega dados do CSV"""
        try:
            if not os.path.exists(self.config['caminho_arquivo']):
                raise FileNotFoundError(f"Arquivo nao encontrado: {self.config['caminho_arquivo']}")
            
            self.df = pd.read_csv(self.config['caminho_arquivo'], encoding='latin1')
            logger.info(f"OK - Dados carregados: {len(self.df)} linhas")
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha ao carregar dados: {e}")
            return False
    
    def padronizar_colunas(self):
        """Padroniza nomes das colunas"""
        mapeamento = {
            'Row ID': 'ID_Linha', 'Order ID': 'ID_Pedido', 'Order Date': 'Data_Pedido',
            'Ship Date': 'Data_Envio', 'Ship Mode': 'Modo_Envio', 'Customer ID': 'ID_Cliente',
            'Customer Name': 'Nome_Cliente', 'Segment': 'Segmento', 'Country': 'Pais',
            'City': 'Cidade', 'State': 'Estado', 'Postal Code': 'Codigo_Postal',
            'Region': 'Regiao', 'Product ID': 'ID_Produto', 'Category': 'Categoria',
            'Sub-Category': 'Sub_Categoria', 'Product Name': 'Nome_Produto',
            'Sales': 'Vendas', 'Quantity': 'Quantidade', 'Discount': 'Desconto',
            'Profit': 'Lucro'
        }
        self.df = self.df.rename(columns=mapeamento)
        logger.info("OK - Colunas padronizadas")
        return True
    
    def tratar_dados(self):
        """Trata dados (datas, nulos, duplicatas)"""
        try:
            # Converter datas
            self.df['Data_Pedido'] = pd.to_datetime(self.df['Data_Pedido'], format='%d-%m-%Y')
            self.df['Data_Envio'] = pd.to_datetime(self.df['Data_Envio'], format='%d-%m-%Y')
            
            # Criar colunas derivadas
            self.df['Valor_Total'] = self.df['Quantidade'] * self.df['Vendas']
            self.df['Ano'] = self.df['Data_Pedido'].dt.year
            self.df['Mes'] = self.df['Data_Pedido'].dt.month
            self.df['Ano_Mes'] = self.df['Data_Pedido'].dt.to_period('M').astype(str)
            self.df['Mes_Nome'] = self.df['Data_Pedido'].dt.month_name()
            self.df['Ticket_Medio'] = self.df['Vendas'] / self.df['Quantidade']
            
            # Tratar nulos
            self.df['Cidade'] = self.df['Cidade'].fillna('Nao Informado')
            self.df['Lucro'] = self.df['Lucro'].fillna(0)
            
            # Padronizar texto
            self.df['Nome_Produto'] = self.df['Nome_Produto'].str.strip().str.title()
            self.df['Regiao'] = self.df['Regiao'].str.upper()
            
            # Remover duplicatas
            duplicatas_antes = self.df.duplicated().sum()
            self.df = self.df.drop_duplicates()
            
            logger.info(f"OK - Dados tratados - Duplicatas removidas: {duplicatas_antes}")
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha no tratamento: {e}")
            return False
    
    def criar_modelo_star_schema(self):
        """Cria modelo Star Schema"""
        try:
            # Dimensão Local
            dim_local = self.df[['Cidade', 'Estado', 'Regiao', 'Pais']].drop_duplicates().reset_index(drop=True)
            dim_local['pk_id_local'] = dim_local.index + 1
            
            # Dimensão Cliente
            cliente_base = self.df[['ID_Cliente', 'Nome_Cliente', 'Segmento', 'Cidade', 'Estado', 'Regiao', 'Pais']].drop_duplicates('ID_Cliente')
            dim_cliente = cliente_base.merge(dim_local, on=['Cidade', 'Estado', 'Regiao', 'Pais'], how='left')
            dim_cliente = dim_cliente[['ID_Cliente', 'Nome_Cliente', 'Segmento', 'pk_id_local']]
            dim_cliente.rename(columns={'pk_id_local': 'fk_id_local'}, inplace=True)
            
            # Dimensão Produto
            dim_produto = self.df[['ID_Produto', 'Nome_Produto', 'Categoria', 'Sub_Categoria']].drop_duplicates('ID_Produto').reset_index(drop=True)
            dim_produto['pk_id_produto'] = dim_produto.index + 1
            dim_produto.rename(columns={'ID_Produto': 'id_produto_original'}, inplace=True)
            
            # Dimensão Data
            dim_data = self.df[['Data_Pedido', 'Ano', 'Mes', 'Mes_Nome']].drop_duplicates('Data_Pedido').reset_index(drop=True)
            dim_data['pk_id_data'] = dim_data.index + 1
            
            # Fato Vendas
            fato_vendas = self.df[['ID_Pedido', 'ID_Cliente', 'ID_Produto', 'Data_Pedido', 'Vendas', 'Quantidade', 'Lucro']].copy()
            
            fato_vendas = fato_vendas.merge(
                dim_produto[['id_produto_original', 'pk_id_produto']].rename(columns={'pk_id_produto': 'fk_id_produto'}),
                left_on='ID_Produto',
                right_on='id_produto_original',
                how='left'
            )
            
            fato_vendas = fato_vendas.merge(
                dim_data[['Data_Pedido', 'pk_id_data']].rename(columns={'pk_id_data': 'fk_id_data'}),
                on='Data_Pedido',
                how='left'
            )
            
            fato_vendas = fato_vendas[['ID_Pedido', 'ID_Cliente', 'fk_id_produto', 'fk_id_data', 'Vendas', 'Quantidade', 'Lucro']]
            fato_vendas.rename(columns={'ID_Pedido': 'id_pedido', 'ID_Cliente': 'id_cliente'}, inplace=True)
            fato_vendas = fato_vendas.drop_duplicates(subset=['id_pedido', 'fk_id_produto'], keep='first')
            
            self.modelo = {
                'dim_local': dim_local,
                'dim_cliente': dim_cliente,
                'dim_produto': dim_produto,
                'dim_data': dim_data,
                'fato_vendas': fato_vendas
            }
            
            logger.info("OK - Modelo Star Schema criado")
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha no modelo: {e}")
            return False
    
    def carregar_banco(self):
        """Carrega dados no MySQL"""
        try:
            with self.conexao.connect() as conn:
                # Limpar tabelas existentes
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
                for tabela in ['fato_vendas', 'dim_cliente', 'dim_local', 'dim_produto', 'dim_data']:
                    conn.execute(text(f"DROP TABLE IF EXISTS {tabela}"))
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
                conn.commit()
            
            # Carregar novas tabelas
            for nome_tabela, df_tabela in self.modelo.items():
                df_tabela.to_sql(nome_tabela, con=self.conexao, if_exists='replace', index=False)
                logger.info(f"  OK - {nome_tabela} carregada - {len(df_tabela)} registros")
            
            logger.info("SUCESSO - Todos os dados carregados!")
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha ao carregar dados: {e}")
            return False
    
    def gerar_relatorio(self):
        """Gera relatório da execução"""
        try:
            # Criar pasta de relatorios se não existir
            relatorio_dir = "relatorios"
            if not os.path.exists(relatorio_dir):
                os.makedirs(relatorio_dir)
            
            relatorio = {
                'data_execucao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'registros_processados': len(self.df) if self.df is not None else 0,
                'status': 'SUCESSO'
            }
            
            # Adicionar contagem das tabelas
            if hasattr(self, 'modelo'):
                for nome, df_tabela in self.modelo.items():
                    relatorio[f'tabela_{nome}'] = len(df_tabela)
            
            # Salvar relatório
            df_relatorio = pd.DataFrame([relatorio])
            arquivo_relatorio = os.path.join(relatorio_dir, f'relatorio_etl_{datetime.now().strftime("%Y%m%d")}.csv')
            df_relatorio.to_csv(arquivo_relatorio, index=False, encoding='utf-8-sig')
            logger.info(f"OK - Relatorio salvo: {arquivo_relatorio}")
            
            return True
        except Exception as e:
            logger.error(f"ERRO - Falha ao gerar relatorio: {e}")
            return False
    
    def executar(self):
        """Executa pipeline completo"""
        inicio = datetime.now()
        logger.info("="*50)
        logger.info("INICIANDO PIPELINE ETL")
        logger.info(f"Inicio: {inicio}")
        logger.info("="*50)
        
        # Executar etapas
        etapas = [
            ("Criando conexao", self.criar_conexao),
            ("Carregando dados", self.carregar_dados),
            ("Padronizando colunas", self.padronizar_colunas),
            ("Tratando dados", self.tratar_dados),
            ("Criando modelo", self.criar_modelo_star_schema),
            ("Carregando banco", self.carregar_banco),
            ("Gerando relatorio", self.gerar_relatorio)
        ]
        
        for nome_etapa, funcao in etapas:
            logger.info(f">>> {nome_etapa}...")
            if not funcao():
                logger.error(f"ERRO - Falha na etapa: {nome_etapa}")
                return False
        
        fim = datetime.now()
        duracao = fim - inicio
        logger.info("="*50)
        logger.info("PIPELINE FINALIZADO COM SUCESSO!")
        logger.info(f"Duracao total: {duracao}")
        logger.info(f"Termino: {fim}")
        logger.info("="*50)
        
        return True

# ============================================
# CONFIGURACAO
# ============================================
def get_config():
    """Retorna configuração do pipeline"""
    return {
        'caminho_arquivo': "C:/Users/Eliane/Downloads/Arquivos Facul/Analise_Chamados/Vendasteste/Superstore.csv",
        'usuario': 'root',
        'senha': 'Limites1007@',
        'host': '127.0.0.1',
        'porta': 3306,
        'banco': 'empresa_analitica'
    }

# ============================================
# EXECUCAO
# ============================================
if __name__ == "__main__":
    config = get_config()
    pipeline = ETLPipeline(config)
    sucesso = pipeline.executar()
    
    if sucesso:
        print("\n" + "="*50)
        print("PROCESSO CONCLUIDO COM SUCESSO!")
        print("="*50)
        print(f"Log salvo em: logs/")
        print(f"Relatorio salvo em: relatorios/")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("ERRO NA EXECUCAO - Verifique os logs!")
        print("="*50)
    
    sys.exit(0 if sucesso else 1)
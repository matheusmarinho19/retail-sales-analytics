import schedule
import time
from datetime import datetime
from etl_pipeline import ETLPipeline, get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def executar_etl():
    """Função wrapper para executar ETL"""
    logger.info(f"🔄 Executando ETL agendado - {datetime.now()}")
    pipeline = ETLPipeline(get_config())
    sucesso = pipeline.executar()
    
    if sucesso:
        logger.info("✅ ETL executado com sucesso")
    else:
        logger.error("❌ Falha na execução do ETL")
    
    return sucesso

def iniciar_agendador():
    """Inicia o agendador de tarefas"""
    
    # Agendar para 23:30 todos os dias
    schedule.every().day.at("23:30").do(executar_etl)
    
    # Opcional: Agendar também para testar durante o dia
    # schedule.every().hour.do(executar_etl)  # A cada hora
    
    logger.info("🚀 Agendador iniciado")
    logger.info("📅 Tarefa agendada para 23:30 diariamente")
    
    # Executar uma vez imediatamente para teste
    logger.info("🧪 Executando teste inicial...")
    executar_etl()
    
    # Loop infinito
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto

if __name__ == "__main__":
    iniciar_agendador()
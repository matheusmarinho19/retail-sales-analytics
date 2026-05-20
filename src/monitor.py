import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from datetime import datetime

class MonitorETL:
    """Monitora e notifica sobre execuções ETL"""
    
    def __init__(self, config_email):
        self.config_email = config_email
    
    def enviar_email(self, assunto, corpo, anexo=None):
        """Envia email de notificação"""
        msg = MIMEMultipart()
        msg['From'] = self.config_email['remetente']
        msg['To'] = self.config_email['destinatario']
        msg['Subject'] = assunto
        
        msg.attach(MIMEText(corpo, 'html'))
        
        try:
            with smtplib.SMTP(self.config_email['smtp_server'], self.config_email['smtp_port']) as server:
                server.starttls()
                server.login(self.config_email['remetente'], self.config_email['senha'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    def gerar_dashboard_status(self):
        """Gera dashboard de status das execuções"""
        # Ler logs
        logs = []
        for arquivo in glob.glob("etl_log_*.log"):
            with open(arquivo, 'r') as f:
                logs.append(f.read())
        
        # Criar relatório
        relatorio = f"""
        <html>
        <head><title>Status ETL - Vendas</title></head>
        <body>
            <h1>📊 Relatório ETL - {datetime.now().strftime('%d/%m/%Y')}</h1>
            <h2>Status: ✅ Executado com sucesso</h2>
            <h3>Detalhes:</h3>
            <ul>
                <li>Última execução: {datetime.now()}</li>
                <li>Próxima execução: Amanhã às 23:30</li>
            </ul>
            <h3>Logs recentes:</h3>
            <pre>{logs[-1] if logs else 'Nenhum log encontrado'}</pre>
        </body>
        </html>
        """
        
        return relatorio

# Integrar com o pipeline
def executar_com_monitoramento():
    pipeline = ETLPipeline(get_config())
    sucesso = pipeline.executar()
    
    monitor = MonitorETL(config_email={
        'remetente': 'etl@empresa.com',
        'destinatario': 'admin@empresa.com',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'senha': 'sua_senha'
    })
    
    if sucesso:
        assunto = "✅ ETL executado com sucesso"
        corpo = monitor.gerar_dashboard_status()
        monitor.enviar_email(assunto, corpo)
    else:
        assunto = "❌ Falha na execução do ETL"
        corpo = "O pipeline ETL falhou. Verificar logs para mais detalhes."
        monitor.enviar_email(assunto, corpo)
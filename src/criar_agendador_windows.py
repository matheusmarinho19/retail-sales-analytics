# criar_agendador_windows.py
import subprocess
import os

def criar_tarefa_agendada():
    """Cria tarefa no Windows Task Scheduler"""
    
    comando = f'''
    schtasks /create /tn "ETL_Vendas_Diario" /tr "{os.path.abspath('executar_etl.bat')}" /sc DAILY /st 23:30 /f
    '''
    
    try:
        subprocess.run(comando, shell=True, check=True)
        print("✅ Tarefa agendada criada para execução diária às 23:30")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar tarefa: {e}")

if __name__ == "__main__":
    criar_tarefa_agendada()
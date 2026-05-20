# run.py - Ponto de entrada único do projeto
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           SISTEMA DE ANÁLISE DE VENDAS - ETL             ║
    ║                                                          ║
    ║  Opções disponíveis:                                     ║
    ║    1. Executar ETL (Carregar dados no MySQL)            ║
    ║    2. Executar Análise Inteligente (Gerar relatórios)   ║
    ║    3. Executar ambos (ETL + Análise)                    ║
    ║    4. Sair                                              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    while True:
        opcao = input("\n👉 Escolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            print("\n🚀 Executando ETL Pipeline...")
            from etl_pipeline import ETLPipeline, get_config
            pipeline = ETLPipeline(get_config())
            pipeline.executar()
            
        elif opcao == '2':
            print("\n🚀 Executando Análise Inteligente...")
            from analise_inteligente import main as analise_main
            analise_main()
            
        elif opcao == '3':
            print("\n🚀 Executando ETL + Análise...")
            print("\n--- ETAPA 1: ETL ---")
            from etl_pipeline import ETLPipeline, get_config
            pipeline = ETLPipeline(get_config())
            if pipeline.executar():
                print("\n--- ETAPA 2: Análise ---")
                from analise_inteligente import main as analise_main
                analise_main()
            else:
                print("❌ ETL falhou, análise não executada")
                
        elif opcao == '4':
            print("👋 Encerrando...")
            break
        else:
            print("❌ Opção inválida! Escolha 1, 2, 3 ou 4")
        
        input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
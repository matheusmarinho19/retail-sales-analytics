@echo off
chcp 65001 > nul
cls

echo ========================================
echo EXECUTANDO ETL PIPELINE
echo Data: %date%
echo Hora: %time%
echo ========================================
echo.

:: Ir para a raiz do projeto
cd /d "C:\Users\Eliane\Downloads\Arquivos Facul\Analise_Chamados\Vendasteste\CETL_Vendas"

:: Executar via run.py
python run.py

echo.
echo ========================================
echo PROCESSO FINALIZADO
echo ========================================
pause
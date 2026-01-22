@echo off
REM Script para iniciar o servidor Django
REM Executar este arquivo diretamente (duplo clique ou via terminal)

echo ========================================
echo   INICIANDO SERVIDOR DJANGO
echo ========================================
echo.

cd /d "C:\1.3 Gestao"

REM Verificar se a venv existe
if not exist "venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Execute primeiro: python -m venv venv
    pause
    exit /b 1
)

echo [OK] Ambiente virtual encontrado
echo.

REM Iniciar servidor
echo Iniciando servidor na porta 8000...
echo Acesse: http://127.0.0.1:8000
echo.
echo Usuario: admin
echo Senha: adm1234@
echo.
echo Pressione CTRL+C para parar o servidor
echo ========================================
echo.

venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

pause

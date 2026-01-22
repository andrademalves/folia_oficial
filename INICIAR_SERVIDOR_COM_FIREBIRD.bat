@echo off
REM Script para configurar Firebird Client e iniciar servidor Django

echo ================================================================================
echo CONFIGURANDO AMBIENTE FIREBIRD + DJANGO
echo ================================================================================

REM Adicionar Firebird Client ao PATH da sessão
set PATH=C:\Firebird\bin;%PATH%
echo [OK] Firebird Client adicionado ao PATH

REM Verificar se porta 8000 está livre
echo.
echo Verificando porta 8000...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [AVISO] Porta 8000 ja esta em uso
    echo [INFO] Encerrando processos Python na porta 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
    timeout /t 2 >nul
)

REM Ativar ambiente virtual
echo.
echo Ativando ambiente virtual Python...
call venv\Scripts\activate.bat

echo.
echo ================================================================================
echo SERVIDOR DJANGO - ACESSO EXTERNO E INTERNO
echo ================================================================================
echo.
echo O servidor estara acessivel em:
echo   - Externo: http://folia.dvrdns.org:8000
echo   - Interno: http://192.168.10.8:8000
echo   - Local:   http://localhost:8000
echo.
echo Configuracoes necessarias:
echo   [OK] ALLOWED_HOSTS configurado
echo   [OK] Firebird Client instalado
echo   [ ] Port Forwarding no roteador (porta 8000 para 192.168.10.8)
echo   [ ] Firewall Windows liberado (execute CONFIGURAR_FIREWALL.bat como Admin)
echo.
echo ================================================================================

REM Iniciar servidor Django em todas as interfaces (0.0.0.0)
echo.
echo Iniciando servidor Django em 0.0.0.0:8000...
echo Pressione Ctrl+C para parar o servidor
echo.
python manage.py runserver 0.0.0.0:8000

pause

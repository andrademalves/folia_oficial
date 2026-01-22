@echo off
REM Script para liberar porta 8000 no Firewall do Windows
REM Execute como Administrador

echo ================================================================================
echo CONFIGURANDO FIREWALL WINDOWS - PORTA 8000
echo ================================================================================

echo.
echo [1] Removendo regra antiga (se existir)...
netsh advfirewall firewall delete rule name="Django Server" >nul 2>&1
netsh advfirewall firewall delete rule name="Django Server Port 8000" >nul 2>&1

echo.
echo [2] Adicionando nova regra para porta 8000...
netsh advfirewall firewall add rule name="Django Server Port 8000" dir=in action=allow protocol=TCP localport=8000

if %errorlevel% equ 0 (
    echo.
    echo [OK] Firewall configurado com sucesso!
    echo [OK] Porta 8000 TCP liberada para entrada
) else (
    echo.
    echo [ERRO] Falha ao configurar firewall
    echo [ERRO] Execute este script como Administrador
    echo.
    echo Clique com botao direito no arquivo e selecione:
    echo "Executar como Administrador"
)

echo.
echo [3] Verificando regra criada...
netsh advfirewall firewall show rule name="Django Server Port 8000"

echo.
echo ================================================================================
echo CONFIGURACAO CONCLUIDA
echo ================================================================================
echo.
echo Porta 8000 agora esta acessivel de:
echo - Rede interna (192.168.10.x)
echo - Internet (via folia.dvrdns.org)
echo.
echo Proximo passo:
echo Configure Port Forwarding no roteador:
echo   Porta externa: 8000
echo   IP interno: 192.168.10.8
echo   Porta interna: 8000
echo   Protocolo: TCP
echo.
pause

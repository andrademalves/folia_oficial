"""
Script para instalar e configurar Firebird Client no Windows
"""
import os
import sys
import urllib.request
import zipfile
import shutil

print("="*80)
print("INSTALADOR FIREBIRD CLIENT - BIBLIOTECA FDB")
print("="*80)

# Detectar arquitetura
import platform
is_64bit = platform.machine().endswith('64')
arch = "x64" if is_64bit else "Win32"

print(f"\n[1] Sistema detectado: Windows {arch}")

# Diretório de instalação
INSTALL_DIR = r"C:\Firebird"
DLL_DIR = os.path.join(INSTALL_DIR, "bin")

print(f"\n[2] Diretório de instalação: {INSTALL_DIR}")

# Criar diretórios
if not os.path.exists(INSTALL_DIR):
    os.makedirs(INSTALL_DIR)
    print(f"    ✓ Criado: {INSTALL_DIR}")

if not os.path.exists(DLL_DIR):
    os.makedirs(DLL_DIR)
    print(f"    ✓ Criado: {DLL_DIR}")

# URLs dos arquivos necessários
print(f"\n[3] Arquivos necessários:")

# fbclient.dll é a DLL principal que o fdb precisa
files_to_download = [
    {
        'name': 'fbclient.dll',
        'url_64': 'https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_x64.zip',
        'url_32': 'https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_Win32.zip',
        'extract_path': 'fbclient.dll'
    }
]

print(f"""
    OPÇÃO MANUAL RECOMENDADA:
    
    1. Baixe o Firebird Client/Embedded:
       64-bit: https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_x64.zip
       32-bit: https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_Win32.zip
    
    2. Extraia o arquivo fbclient.dll para: {DLL_DIR}
    
    3. Adicione {DLL_DIR} ao PATH do sistema
    
    4. OU copie fbclient.dll para: C:\\Windows\\System32
    
    ALTERNATIVA RÁPIDA (apenas DLL):
    
    Execute este PowerShell como Administrador:
""")

# Gerar script PowerShell para download direto
ps_script = f"""
# Script PowerShell para baixar fbclient.dll
$url = "https://github.com/FirebirdSQL/firebird/releases/download/v3.0.10/Firebird-3.0.10.33601-0_{'x64' if is_64bit else 'Win32'}.zip"
$zipFile = "$env:TEMP\\firebird_client.zip"
$extractPath = "$env:TEMP\\firebird_extract"

Write-Host "Baixando Firebird Client..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $zipFile

Write-Host "Extraindo arquivo..." -ForegroundColor Yellow
Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

Write-Host "Copiando fbclient.dll..." -ForegroundColor Yellow
Copy-Item "$extractPath\\fbclient.dll" -Destination "{DLL_DIR}\\fbclient.dll" -Force

Write-Host "Limpando arquivos temporários..." -ForegroundColor Yellow
Remove-Item $zipFile -Force
Remove-Item $extractPath -Recurse -Force

Write-Host "✓ Firebird Client instalado em: {DLL_DIR}" -ForegroundColor Green
Write-Host "✓ Adicione ao PATH ou copie para C:\\Windows\\System32" -ForegroundColor Green
"""

ps_file = "instalar_firebird_client.ps1"
with open(ps_file, 'w', encoding='utf-8') as f:
    f.write(ps_script)

print(f"""
    Salvo script PowerShell: {ps_file}
    
    Execute como Administrador:
    PowerShell -ExecutionPolicy Bypass -File {ps_file}
""")

# Verificar se fbclient.dll já existe
fbclient_paths = [
    os.path.join(DLL_DIR, 'fbclient.dll'),
    r'C:\Windows\System32\fbclient.dll',
    r'C:\Windows\SysWOW64\fbclient.dll',
]

print(f"\n[4] Verificando se fbclient.dll já está instalada...")
found = False
for path in fbclient_paths:
    if os.path.exists(path):
        print(f"    ✓ Encontrada em: {path}")
        found = True

if not found:
    print(f"    ✗ fbclient.dll NÃO encontrada")
    print(f"\n    AÇÃO NECESSÁRIA:")
    print(f"    1. Execute o script PowerShell como administrador")
    print(f"    2. OU baixe manualmente e coloque em {DLL_DIR}")
    print(f"    3. OU copie para C:\\Windows\\System32")

# Configurar variável de ambiente para fdb encontrar a DLL
print(f"\n[5] Configurando variável de ambiente FB_CLIENT...")

# Criar script para adicionar ao PATH permanente
batch_script = f"""@echo off
echo Adicionando Firebird Client ao PATH...
setx PATH "%PATH%;{DLL_DIR}"
echo.
echo ✓ PATH atualizado!
echo ✓ Reinicie o terminal/IDE para aplicar as mudanças
pause
"""

bat_file = "adicionar_firebird_ao_path.bat"
with open(bat_file, 'w', encoding='utf-8') as f:
    f.write(batch_script)

print(f"    Salvo script: {bat_file}")
print(f"    Execute como Administrador para adicionar ao PATH permanente")

# Tentar configurar para sessão atual
os.environ['PATH'] = f"{DLL_DIR};{os.environ.get('PATH', '')}"
print(f"    ✓ PATH atualizado para sessão atual")

# Informar ao fdb onde está a DLL
os.environ['FB_CLIENT'] = os.path.join(DLL_DIR, 'fbclient.dll')
print(f"    ✓ FB_CLIENT configurado: {os.environ['FB_CLIENT']}")

print(f"\n{'='*80}")
print("PRÓXIMOS PASSOS:")
print(f"{'='*80}")
print(f"""
1. BAIXAR FBCLIENT.DLL:
   Execute como Administrador:
   PowerShell -ExecutionPolicy Bypass -File {ps_file}

2. ADICIONAR AO PATH (opcional):
   Execute como Administrador:
   {bat_file}

3. OU copiar manualmente:
   Copie fbclient.dll para C:\\Windows\\System32

4. TESTAR CONEXÃO:
   python testar_conexao_firebird.py

CONFIGURAÇÃO ALTERNATIVA (sem download):

Se você já tem Firebird instalado localmente:
   - Encontre fbclient.dll (geralmente em C:\\Program Files\\Firebird\\)
   - Copie para {DLL_DIR}
   - OU configure: set FB_CLIENT=C:\\caminho\\para\\fbclient.dll

""")

print("="*80)

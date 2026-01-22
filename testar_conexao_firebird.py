"""
Script para testar e diagnosticar conexão com Firebird do Futura
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

print("="*80)
print("TESTE DE CONEXÃO FIREBIRD - SISTEMA FUTURA")
print("="*80)

# Verificar se fdb está instalado
print("\n[1] Verificando biblioteca fdb...")
try:
    import fdb
    print(f"    ✓ FDB instalado - Versão: {fdb.__version__}")
except ImportError as e:
    print(f"    ✗ FDB NÃO instalado!")
    print(f"    Erro: {e}")
    print(f"\n    Execute: pip install fdb")
    sys.exit(1)

# Verificar configuração no banco
print("\n[2] Verificando configuração no banco de dados...")
from importacoes.models import ConfiguracaoFirebird

try:
    config = ConfiguracaoFirebird.get_config()
    print(f"    ✓ Configuração encontrada:")
    print(f"      Host: {config.host}")
    print(f"      Porta: {config.port}")
    print(f"      Database: {config.database}")
    print(f"      Usuário: {config.user}")
    print(f"      Senha: {'*' * len(config.password) if config.password else '(vazio)'}")
    print(f"      Ativo: {config.ativo}")
except Exception as e:
    print(f"    ✗ Erro ao buscar configuração: {e}")
    sys.exit(1)

# Teste de conectividade de rede
print(f"\n[3] Testando conectividade de rede com {config.host}...")
import subprocess

try:
    # Ping test (1 pacote, timeout 5 segundos)
    result = subprocess.run(
        ['ping', '-n', '1', '-w', '5000', config.host],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print(f"    ✓ Host {config.host} está acessível via ping")
    else:
        print(f"    ✗ Host {config.host} NÃO responde ao ping")
        print(f"    Isso pode indicar:")
        print(f"      - Firewall bloqueando ICMP")
        print(f"      - Host offline ou inacessível")
        print(f"      - Rede sem rota para o host")
except subprocess.TimeoutExpired:
    print(f"    ⚠ Timeout ao fazer ping em {config.host}")
except Exception as e:
    print(f"    ⚠ Não foi possível testar ping: {e}")

# Teste de porta (telnet-like)
print(f"\n[4] Testando conectividade na porta {config.port}...")
import socket

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((config.host, config.port))
    sock.close()
    
    if result == 0:
        print(f"    ✓ Porta {config.port} está aberta e acessível")
    else:
        print(f"    ✗ Porta {config.port} está FECHADA ou inacessível")
        print(f"    Códigos de erro comuns:")
        print(f"      10060: Connection timeout (firewall bloqueando)")
        print(f"      10061: Connection refused (serviço não rodando)")
        print(f"    Código retornado: {result}")
except socket.timeout:
    print(f"    ✗ Timeout ao conectar na porta {config.port}")
    print(f"    Firewall pode estar bloqueando a conexão")
except Exception as e:
    print(f"    ✗ Erro ao testar porta: {e}")

# Teste de conexão Firebird
print(f"\n[5] Testando conexão com Firebird...")
try:
    from importacoes.firebird_utils import FirebirdConnector
    
    connector = FirebirdConnector()
    sucesso = connector.conectar()
    
    if sucesso:
        print(f"\n    ✓✓✓ CONEXÃO ESTABELECIDA COM SUCESSO! ✓✓✓")
        print(f"    Versão do servidor: {connector.conn.server_version}")
        
        # Testar uma query simples
        print(f"\n[6] Testando query simples...")
        try:
            cursor = connector.conn.cursor()
            cursor.execute("SELECT FIRST 1 * FROM RDB$DATABASE")
            result = cursor.fetchone()
            cursor.close()
            print(f"    ✓ Query executada com sucesso!")
            
        except Exception as e:
            print(f"    ✗ Erro ao executar query: {e}")
        
        connector.desconectar()
        
    else:
        print(f"\n    ✗✗✗ FALHA NA CONEXÃO COM FIREBIRD ✗✗✗")
        
except Exception as e:
    print(f"    ✗ Erro ao tentar conectar: {e}")
    import traceback
    print(f"\n    Stack trace completo:")
    traceback.print_exc()

# Resumo e sugestões
print(f"\n{'='*80}")
print("RESUMO E SUGESTÕES")
print(f"{'='*80}")

print(f"""
VERIFICAÇÕES A FAZER:

1. FIREWALL NO SERVIDOR FIREBIRD:
   - A porta 3050 precisa estar aberta
   - Verifique regras de entrada no Windows Firewall

2. FIREBIRD SERVER:
   - Verifique se o serviço está rodando
   - No servidor, execute: services.msc
   - Procure por "Firebird Server"

3. CONFIGURAÇÃO DO BANCO:
   - Caminho: {config.database}
   - Confirme se o arquivo .FDB existe neste caminho
   - Verifique permissões de leitura

4. CREDENCIAIS:
   - Usuário: {config.user}
   - Teste login manual no servidor Firebird

5. REDE:
   - Host: {config.host}
   - Certifique-se que há rota de rede até o servidor
   - Se estiver em VPN, verifique se está conectado

COMANDOS ÚTEIS NO SERVIDOR FIREBIRD:
   - netstat -an | findstr :3050  (verificar se porta está em LISTEN)
   - gstat -h {config.database}  (informações do banco)
""")

print("="*80)

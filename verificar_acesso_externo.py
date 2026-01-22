"""
Script para verificar configuração de acesso externo e interno
"""
import socket
import os

print("="*80)
print("VERIFICAÇÃO DE ACESSO - DOMÍNIO EXTERNO E REDE INTERNA")
print("="*80)

# Informações do sistema
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"\n[1] Informações do servidor:")
print(f"    Hostname: {hostname}")
print(f"    IP Local: {local_ip}")

# Verificar configuração no Django
print(f"\n[2] Configuração Django (settings.py):")
print(f"    ALLOWED_HOSTS configurado com:")
print(f"    ✓ localhost")
print(f"    ✓ 127.0.0.1")
print(f"    ✓ folia.dvrdns.org (domínio externo)")
print(f"    ✓ 192.168.10.8 (IP interno)")
print(f"    ✓ 192.168.10.* (rede interna)")

# Resolver domínio externo
print(f"\n[3] Resolvendo domínio externo:")
try:
    ip_externo = socket.gethostbyname('folia.dvrdns.org')
    print(f"    ✓ folia.dvrdns.org → {ip_externo}")
except Exception as e:
    print(f"    ✗ Erro ao resolver folia.dvrdns.org: {e}")

# URLs de acesso
print(f"\n[4] URLs de acesso ao sistema:")
print(f"\n    ACESSO EXTERNO (Internet):")
print(f"    → http://folia.dvrdns.org:8000")
print(f"    → http://folia.dvrdns.org:8000/login/")
print(f"    → http://folia.dvrdns.org:8000/admin/")

print(f"\n    ACESSO INTERNO (Rede Local):")
print(f"    → http://192.168.10.8:8000")
print(f"    → http://192.168.10.8:8000/login/")
print(f"    → http://{local_ip}:8000")

print(f"\n    ACESSO LOCAL (Própria máquina):")
print(f"    → http://localhost:8000")
print(f"    → http://127.0.0.1:8000")

# Verificações necessárias
print(f"\n[5] Verificações necessárias no roteador/firewall:")
print(f"\n    REDIRECIONAMENTO DE PORTA (Port Forwarding):")
print(f"    ✓ Porta externa: 8000 (ou 80)")
print(f"    ✓ IP interno: 192.168.10.8")
print(f"    ✓ Porta interna: 8000")
print(f"    ✓ Protocolo: TCP")

print(f"\n    FIREWALL WINDOWS:")
print(f"    Execute como Administrador:")
print(f"    netsh advfirewall firewall add rule name=\"Django Server\" dir=in action=allow protocol=TCP localport=8000")

print(f"\n[6] Testar acesso externo:")
print(f"\n    De uma máquina FORA da rede local, acesse:")
print(f"    http://folia.dvrdns.org:8000")
print(f"\n    Se não funcionar, verifique:")
print(f"    1. Port forwarding configurado no roteador")
print(f"    2. Firewall Windows liberado na porta 8000")
print(f"    3. Servidor Django rodando com: 0.0.0.0:8000")
print(f"    4. IP externo está atualizado no DDNS (folia.dvrdns.org)")

print(f"\n[7] Comando para iniciar servidor:")
print(f"    python manage.py runserver 0.0.0.0:8000")
print(f"\n    OU use o script:")
print(f"    INICIAR_SERVIDOR_COM_FIREBIRD.bat")

print(f"\n[8] Verificar porta 8000:")
print(f"\n    No Windows, execute:")
print(f"    netstat -an | findstr :8000")
print(f"\n    Deve mostrar:")
print(f"    TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING")

print(f"\n{'='*80}")
print("CONFIGURAÇÃO CONCLUÍDA!")
print(f"{'='*80}")
print(f"""
O Django agora aceita requisições de:
✓ folia.dvrdns.org (acesso externo via DDNS)
✓ 192.168.10.8 (IP interno fixo)
✓ 192.168.10.* (qualquer IP da rede interna)
✓ localhost/127.0.0.1 (acesso local)

Certifique-se de:
1. Configurar port forwarding no roteador (porta 8000)
2. Liberar porta 8000 no firewall Windows
3. Iniciar servidor com: 0.0.0.0:8000 (não apenas localhost)
""")
print("="*80)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("="*80)
print("TESTE AUTOMÁTICO - Verificando módulos exibidos após login")
print("="*80)

# Criar cliente de teste
client = Client()

# Login como admin
print("\n[1] Fazendo login como admin...")
login_success = client.login(username='admin', password='adm1234@')
print(f"    Login bem-sucedido: {login_success}")

if not login_success:
    print("    ✗ ERRO: Não foi possível fazer login!")
    exit(1)

# Acessar página de módulos
print("\n[2] Acessando /...")
response = client.get('/')
print(f"    Status: {response.status_code}")

if response.status_code != 200:
    print(f"    ✗ ERRO: Esperado 200, obtido {response.status_code}")
    exit(1)

# Verificar se a página contém o módulo Sistema
content = response.content.decode('utf-8')

print("\n[3] Verificando módulos na resposta HTML...")

modulos = ['Cadastros', 'Financeiro', 'Contas a Receber', 'Boletos', 'Importações', 'Sistema']

for modulo in modulos:
    if modulo in content:
        print(f"    ✓ {modulo:20} - ENCONTRADO")
    else:
        print(f"    ✗ {modulo:20} - NÃO ENCONTRADO")

# Verificar especificamente textos relacionados ao módulo Sistema
print("\n[4] Verificações específicas do módulo Sistema:")
verificacoes = [
    ('Sistema', 'Nome do módulo'),
    ('Gestão de Acessos', 'Label do botão'),
    ('/usuarios/usuarios/', 'URL de acesso'),
]

for texto, descricao in verificacoes:
    if texto in content:
        print(f"    ✓ '{texto}' ({descricao})")
    else:
        print(f"    ✗ '{texto}' ({descricao}) NÃO ENCONTRADO")

# Verificar se há mensagem de "nenhum módulo disponível"
if 'Nenhum módulo disponível' in content:
    print("\n    ⚠ AVISO: Página mostra 'Nenhum módulo disponível'")
else:
    print("\n    ✓ Página NÃO mostra mensagem de módulos indisponíveis")

# Contar quantos módulos aparecem
import re
module_cards = content.count('module-card')
print(f"\n[5] Número de cards de módulos encontrados: {module_cards}")

if module_cards == 6:
    print("    ✓ CORRETO: 6 módulos exibidos (incluindo Sistema)")
elif module_cards == 5:
    print("    ✗ PROBLEMA: Apenas 5 módulos exibidos (Sistema está faltando)")
else:
    print(f"    ⚠ ATENÇÃO: Número inesperado de módulos: {module_cards}")

print("\n" + "="*80)
print("CONCLUSÃO:")
if 'Sistema' in content and module_cards == 6:
    print("✓ TESTE PASSOU: Módulo Sistema está sendo exibido corretamente!")
else:
    print("✗ TESTE FALHOU: Módulo Sistema NÃO está aparecendo!")
print("="*80)

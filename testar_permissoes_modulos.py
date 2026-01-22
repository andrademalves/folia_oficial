"""
Script de teste automático para verificar permissões de todos os módulos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from usuarios.models import Menu, Modulo, PermissaoMenu

print("="*80)
print("TESTE DE PERMISSÕES - TODOS OS MÓDULOS")
print("="*80)

# Criar usuário de teste
username = 'teste_permissoes'
try:
    user = User.objects.get(username=username)
    print(f"\n[1] Usuário '{username}' já existe")
except User.DoesNotExist:
    user = User.objects.create_user(username=username, password='teste123')
    print(f"\n[1] Usuário '{username}' criado")

user.is_active = True
user.save()

# Limpar permissões antigas
PermissaoMenu.objects.filter(usuario=user).delete()

# Dar permissão de visualizar para o menu principal de cada módulo
modulos = Modulo.objects.filter(ativo=True).order_by('ordem')

print(f"\n[2] Configurando permissões para {modulos.count()} módulos...\n")

menus_testados = []
for modulo in modulos:
    # Pegar o primeiro menu (dashboard) de cada módulo
    menu_principal = Menu.objects.filter(
        modulo=modulo, 
        ativo=True,
        menu_pai__isnull=True
    ).order_by('ordem').first()
    
    if menu_principal:
        # Criar permissão
        PermissaoMenu.objects.create(
            usuario=user,
            menu=menu_principal,
            pode_visualizar=True,
            pode_criar=False,
            pode_editar=False,
            pode_excluir=False
        )
        menus_testados.append((modulo.nome, menu_principal.url, menu_principal.nome))
        print(f"  ✓ {modulo.nome:20} - Permissão para '{menu_principal.nome}' ({menu_principal.url})")

# Testar acesso a cada URL
print(f"\n[3] Testando acesso a {len(menus_testados)} URLs...\n")

client = Client()
login_ok = client.login(username=username, password='teste123')

if not login_ok:
    print("  ✗ ERRO: Falha no login!")
    exit(1)

resultados = {'ok': 0, 'erro': 0, 'detalhes': []}

for modulo_nome, url, menu_nome in menus_testados:
    try:
        response = client.get(url, follow=True)
        
        # Verificar se não foi redirecionado para home (sem permissão)
        if '/login' in response.request['PATH_INFO']:
            status = '✗ ERRO'
            detalhe = 'Redirecionado para login'
            resultados['erro'] += 1
        elif 'Menu não encontrado' in str(response.content):
            status = '✗ ERRO'
            detalhe = 'Menu não encontrado'
            resultados['erro'] += 1
        elif 'não tem permissão' in str(response.content):
            status = '✗ ERRO'
            detalhe = 'Sem permissão'
            resultados['erro'] += 1
        elif response.status_code == 200:
            status = '✓ OK'
            detalhe = f'Status {response.status_code}'
            resultados['ok'] += 1
        else:
            status = '⚠ AVISO'
            detalhe = f'Status {response.status_code}'
            resultados['erro'] += 1
            
        resultados['detalhes'].append({
            'modulo': modulo_nome,
            'url': url,
            'menu': menu_nome,
            'status': status,
            'detalhe': detalhe
        })
        
        print(f"  {status:10} | {modulo_nome:20} | {url:30} | {detalhe}")
        
    except Exception as e:
        status = '✗ EXCEPTION'
        detalhe = str(e)[:50]
        resultados['erro'] += 1
        resultados['detalhes'].append({
            'modulo': modulo_nome,
            'url': url,
            'menu': menu_nome,
            'status': status,
            'detalhe': detalhe
        })
        print(f"  {status:10} | {modulo_nome:20} | {url:30} | {detalhe}")

# Resumo
print(f"\n{'='*80}")
print("RESUMO DOS TESTES")
print(f"{'='*80}")
print(f"\n  Total testado: {len(menus_testados)}")
print(f"  ✓ Sucesso: {resultados['ok']}")
print(f"  ✗ Falhas: {resultados['erro']}")

if resultados['erro'] > 0:
    print(f"\n  FALHAS ENCONTRADAS:")
    for r in resultados['detalhes']:
        if '✗' in r['status'] or '⚠' in r['status']:
            print(f"    - {r['modulo']:20} ({r['url']}) - {r['detalhe']}")

print(f"\n{'='*80}")

# Limpar usuário de teste
user.delete()
print(f"\nUsuário de teste '{username}' removido.")
print(f"{'='*80}")

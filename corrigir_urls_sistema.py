import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Menu

print("="*80)
print("CORRIGINDO URLs DO MÓDULO SISTEMA")
print("="*80)

# Corrigir URLs dos menus do módulo Sistema
correcoes = [
    ('/usuarios/usuarios/', '/usuarios/'),
    ('/usuarios/usuarios/criar/', '/usuarios/criar/'),
]

print("\nAplicando correções:\n")

for url_antiga, url_nova in correcoes:
    menus = Menu.objects.filter(url=url_antiga)
    count = menus.count()
    
    if count > 0:
        menus.update(url=url_nova)
        print(f"✓ {url_antiga:35} → {url_nova:25} ({count} menu(s))")
    else:
        print(f"  {url_antiga:35} - Não encontrado")

print("\n" + "="*80)
print("VERIFICANDO URLS DO MÓDULO SISTEMA")
print("="*80)

menus_sistema = Menu.objects.filter(modulo__nome='Sistema', ativo=True).order_by('ordem')

print(f"\nTotal de menus ativos: {menus_sistema.count()}\n")

for m in menus_sistema:
    print(f"  {m.nome:30} → {m.url}")

print("\n" + "="*80)
print("✓ URLs corrigidas com sucesso!")
print("="*80)

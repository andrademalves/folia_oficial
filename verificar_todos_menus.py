import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Menu, Modulo

print("="*80)
print("VERIFICANDO MENUS DE TODOS OS MÓDULOS")
print("="*80)

modulos = Modulo.objects.filter(ativo=True).order_by('ordem')

for modulo in modulos:
    print(f"\n{'='*80}")
    print(f"MÓDULO: {modulo.nome}")
    print(f"{'='*80}")
    
    menus = Menu.objects.filter(modulo=modulo, ativo=True, menu_pai__isnull=True).order_by('ordem')
    
    if menus.count() == 0:
        print("  ⚠ Nenhum menu encontrado")
    else:
        print(f"\nTotal de menus principais: {menus.count()}\n")
        for m in menus:
            print(f"  ID: {m.id:3} | URL: {m.url:40} | Nome: {m.nome}")

print("\n" + "="*80)

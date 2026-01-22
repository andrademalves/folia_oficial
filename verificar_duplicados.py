import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo

print("="*80)
print("VERIFICANDO DUPLICAÇÃO DE MÓDULOS")
print("="*80)

modulos = Modulo.objects.all().order_by('ordem', 'id')

print(f"\nTotal de módulos no banco: {modulos.count()}\n")

for m in modulos:
    print(f"ID={m.id:3} | Ordem={m.ordem} | Ativo={m.ativo} | Nome={m.nome:30} | Ícone={m.icone or 'N/A'}")

print("\n" + "="*80)
print("VERIFICANDO MÓDULOS ATIVOS")
print("="*80)

ativos = Modulo.objects.filter(ativo=True).order_by('ordem')
print(f"\nTotal de módulos ativos: {ativos.count()}\n")

for m in ativos:
    menus_count = m.menus.filter(ativo=True, menu_pai__isnull=True).count()
    print(f"Ordem={m.ordem} | {m.nome:30} | Menus principais: {menus_count}")

# Verificar duplicados por nome
print("\n" + "="*80)
print("VERIFICANDO DUPLICATAS POR NOME")
print("="*80)

from django.db.models import Count

duplicados = Modulo.objects.values('nome').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicados:
    print(f"\n⚠ ENCONTRADAS {duplicados.count()} DUPLICATAS:\n")
    for dup in duplicados:
        print(f"  Nome: {dup['nome']} - Quantidade: {dup['count']}")
        mods = Modulo.objects.filter(nome=dup['nome'])
        for m in mods:
            print(f"    → ID={m.id}, ativo={m.ativo}, ordem={m.ordem}")
else:
    print("\n✓ Nenhuma duplicata encontrada")

print("\n" + "="*80)

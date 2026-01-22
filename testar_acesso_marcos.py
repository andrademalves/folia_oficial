#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar acesso do usuário marcos ao módulo Financeiro
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Menu, Modulo, PermissaoMenu
from usuarios.decorators import encontrar_menu

print("=" * 80)
print("TESTE DE ACESSO - USUÁRIO MARCOS AO FINANCEIRO")
print("=" * 80)

# Buscar usuário
try:
    user = User.objects.get(username='marcos')
    print(f"\n✓ Usuário encontrado: {user.username}")
    print(f"  - Superusuário: {user.is_superuser}")
    print(f"  - Ativo: {user.is_active}")
except User.DoesNotExist:
    print("\n✗ Usuário 'marcos' não encontrado!")
    exit(1)

# Testar busca de menu com 'financeiro'
print("\n" + "-" * 80)
print("TESTE 1: Buscar menu com 'financeiro' (como está nas views)")
print("-" * 80)

menu = encontrar_menu('financeiro')
if menu:
    print(f"✓ Menu encontrado: {menu.nome}")
    print(f"  - URL: {menu.url}")
    print(f"  - Módulo: {menu.modulo.nome}")
    print(f"  - Ativo: {menu.ativo}")
else:
    print("✗ Menu NÃO encontrado!")

# Verificar permissões do usuário para esse menu
print("\n" + "-" * 80)
print("TESTE 2: Verificar permissões do marcos para esse menu")
print("-" * 80)

if menu:
    # Permissão direta
    perm_direta = PermissaoMenu.objects.filter(
        usuario=user,
        menu=menu,
        pode_visualizar=True
    ).first()
    
    if perm_direta:
        print(f"✓ Permissão direta encontrada!")
        print(f"  - Tipo: {perm_direta.tipo}")
        print(f"  - Pode visualizar: {perm_direta.pode_visualizar}")
        print(f"  - Pode criar: {perm_direta.pode_criar}")
        print(f"  - Pode editar: {perm_direta.pode_editar}")
        print(f"  - Pode excluir: {perm_direta.pode_excluir}")
    else:
        print("✗ Permissão direta NÃO encontrada")
        
        # Verificar se tem permissão para QUALQUER menu do Financeiro
        perms_financeiro = PermissaoMenu.objects.filter(
            usuario=user,
            menu__modulo__nome='Financeiro',
            pode_visualizar=True
        )
        
        print(f"\n  Permissões para outros menus do Financeiro: {perms_financeiro.count()}")
        for p in perms_financeiro:
            print(f"    - {p.menu.nome} ({p.menu.url})")

# Testar todas as possíveis buscas
print("\n" + "-" * 80)
print("TESTE 3: Testar diferentes formas de buscar")
print("-" * 80)

testes = [
    'financeiro',
    '/financeiro/',
    '/financeiro/dashboard/',
    'Financeiro',
]

for teste in testes:
    menu_teste = encontrar_menu(teste)
    if menu_teste:
        print(f"  ✓ '{teste}' → {menu_teste.nome} ({menu_teste.url})")
    else:
        print(f"  ✗ '{teste}' → Não encontrado")

print("\n" + "=" * 80)
print("CONCLUSÃO")
print("=" * 80)

if menu and perm_direta:
    print("✓ TUDO OK! Usuário marcos DEVERIA ter acesso ao Financeiro")
    print("\nSe está dando erro, o problema pode ser:")
    print("  1. Cache do Django")
    print("  2. Sessão do usuário desatualizada")
    print("  3. Erro na view específica que está sendo acessada")
elif menu and not perm_direta:
    print("⚠ PROBLEMA PARCIAL!")
    print(f"  - Menu '{menu.nome}' foi encontrado")
    print("  - Mas usuário marcos NÃO tem permissão para esse menu específico")
    print("  - Tem permissões para outros menus do Financeiro")
else:
    print("✗ ERRO! Menu não foi encontrado pela função encontrar_menu()")
    
print("\n" + "=" * 80)

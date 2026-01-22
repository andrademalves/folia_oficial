#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico: Por que o módulo Sistema não aparece
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu
from django.contrib.auth.models import User

print('=' * 70)
print('DIAGNÓSTICO: MÓDULO SISTEMA')
print('=' * 70)

# Verificar módulo
print('\n[1] Verificando módulo Sistema...')
try:
    modulo = Modulo.objects.get(nome='Sistema')
    print(f'    Nome: {modulo.nome}')
    print(f'    Ativo: {modulo.ativo}')
    print(f'    Ordem: {modulo.ordem}')
    print(f'    Ícone: {modulo.icone}')
except Modulo.DoesNotExist:
    print('    [ERRO] Módulo Sistema não encontrado!')
    modulo = None

# Verificar menus
if modulo:
    print('\n[2] Verificando menus do módulo Sistema...')
    menus = Menu.objects.filter(modulo=modulo)
    print(f'    Total de menus: {menus.count()}')
    print(f'    Menus ativos: {menus.filter(ativo=True).count()}')
    
    if menus.exists():
        print('\n    Lista de menus:')
        for menu in menus:
            status = 'ATIVO' if menu.ativo else 'INATIVO'
            print(f'      [{status}] {menu.nome} -> {menu.url}')
    else:
        print('    [ERRO] Nenhum menu encontrado!')

# Verificar usuário admin
print('\n[3] Verificando usuário admin...')
try:
    admin = User.objects.get(username='admin')
    print(f'    Username: {admin.username}')
    print(f'    Superusuário: {admin.is_superuser}')
    print(f'    Staff: {admin.is_staff}')
    print(f'    Ativo: {admin.is_active}')
except User.DoesNotExist:
    print('    [ERRO] Usuário admin não encontrado!')

# Verificar todos os módulos ativos
print('\n[4] Todos os módulos ativos no sistema:')
modulos_ativos = Modulo.objects.filter(ativo=True).order_by('ordem')
for mod in modulos_ativos:
    menus_count = Menu.objects.filter(modulo=mod, ativo=True).count()
    print(f'    [{mod.ordem:02d}] {mod.nome} ({menus_count} menus)')

print('\n' + '=' * 70)
print('DIAGNÓSTICO COMPLETO')
print('=' * 70)

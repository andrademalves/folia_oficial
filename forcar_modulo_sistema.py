#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Garantir que módulo Sistema aparece para admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu

print('=' * 70)
print('GARANTINDO VISIBILIDADE DO MÓDULO SISTEMA')
print('=' * 70)

# Atualizar módulo Sistema
modulo, created = Modulo.objects.update_or_create(
    nome='Sistema',
    defaults={
        'descricao': 'Gestão de Usuários e Permissões',
        'icone': 'fa-users-cog',
        'ordem': 6,
        'ativo': True,
    }
)

print(f'\n[OK] Módulo Sistema:')
print(f'    Ativo: {modulo.ativo}')
print(f'    Ordem: {modulo.ordem}')

# Limpar e recriar menus
Menu.objects.filter(modulo=modulo).delete()
print('\n[INFO] Menus antigos removidos')

menus = [
    {
        'nome': 'Gestão de Usuários',
        'url': '/usuarios/usuarios/',
        'icone': 'fa-users',
        'ordem': 1,
    },
    {
        'nome': 'Criar Usuário',
        'url': '/usuarios/usuarios/criar/',
        'icone': 'fa-user-plus',
        'ordem': 2,
    },
    {
        'nome': 'Admin Django',
        'url': '/admin/',
        'icone': 'fa-cog',
        'ordem': 3,
    },
]

print('\n[INFO] Criando menus:')
for menu_data in menus:
    menu = Menu.objects.create(
        modulo=modulo,
        nome=menu_data['nome'],
        url=menu_data['url'],
        icone=menu_data['icone'],
        ordem=menu_data['ordem'],
        ativo=True,
    )
    print(f'  [+] {menu.nome} -> {menu.url}')

print('\n' + '=' * 70)
print('[OK] MÓDULO SISTEMA CONFIGURADO E VISÍVEL!')
print('=' * 70)
print('\nOrdem de exibição dos módulos:')
print('  1. Cadastros')
print('  2. Financeiro')
print('  3. Contas a Receber')
print('  4. Boletos')
print('  5. Importações')
print('  6. Sistema  ← AQUI!')
print('\nFaça LOGOUT e LOGIN novamente, ou pressione CTRL+F5')
print('O módulo Sistema aparecerá no painel inicial!')
print('')

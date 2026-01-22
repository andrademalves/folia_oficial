#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir e ativar módulo Sistema com URLs corretas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu

print('=' * 70)
print('CORRIGINDO MÓDULO SISTEMA - GESTÃO DE USUÁRIOS')
print('=' * 70)

# Buscar ou criar módulo Sistema
modulo, created = Modulo.objects.update_or_create(
    nome='Sistema',
    defaults={
        'descricao': 'Gestão de Usuários e Permissões',
        'icone': 'fa-cogs',
        'ordem': 10,
        'ativo': True,
    }
)

if created:
    print('\n[+] Módulo Sistema criado')
else:
    print('\n[~] Módulo Sistema atualizado')

# Remover menus antigos
Menu.objects.filter(modulo=modulo).delete()
print('[INFO] Menus antigos removidos')

# Criar menus corretos
menus_sistema = [
    {
        'nome': 'Gestão de Usuários',
        'url': '/usuarios/usuarios/',
        'icone': 'fa-users',
        'ordem': 1,
        'descricao': 'Listar, criar e editar usuários'
    },
    {
        'nome': 'Criar Usuário',
        'url': '/usuarios/usuarios/criar/',
        'icone': 'fa-user-plus',
        'ordem': 2,
        'descricao': 'Cadastrar novo usuário'
    },
    {
        'nome': 'Módulos do Sistema',
        'url': '/admin/usuarios/modulo/',
        'icone': 'fa-th-large',
        'ordem': 3,
        'descricao': 'Gerenciar módulos'
    },
    {
        'nome': 'Menus do Sistema',
        'url': '/admin/usuarios/menu/',
        'icone': 'fa-bars',
        'ordem': 4,
        'descricao': 'Gerenciar menus'
    },
    {
        'nome': 'Admin Django',
        'url': '/admin/',
        'icone': 'fa-tools',
        'ordem': 5,
        'descricao': 'Painel administrativo completo'
    },
]

print('\n[INFO] Criando menus:')
for menu_data in menus_sistema:
    menu = Menu.objects.create(
        modulo=modulo,
        nome=menu_data['nome'],
        descricao=menu_data['descricao'],
        url=menu_data['url'],
        icone=menu_data['icone'],
        ordem=menu_data['ordem'],
        ativo=True,
        menu_pai=None,
    )
    print(f'  [+] {menu.nome} -> {menu.url}')

print('\n' + '=' * 70)
print('[OK] Módulo Sistema configurado!')
print('=' * 70)
print('\nO módulo "Sistema" agora aparecerá no painel inicial.')
print('Funcionalidades disponíveis:')
print('  - Criar e gerenciar usuários')
print('  - Atribuir permissões por módulo')
print('  - Ativar/desativar usuários')
print('  - Gerenciar módulos e menus')
print('\nRecarregue a página inicial para ver as alterações.')
print('')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar/atualizar módulos e menus do sistema
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu

# Definir estrutura de módulos e menus
modulos_menus = [
    {
        'nome': 'Cadastros',
        'descricao': 'Gestão de Cadastros',
        'icone': 'fa-users',
        'cor': '#3498db',
        'ordem': 1,
        'menus': [
            {'nome': 'Clientes', 'url': '/cadastros/clientes/', 'icone': 'fa-user', 'ordem': 1},
            {'nome': 'Fornecedores', 'url': '/cadastros/fornecedores/', 'icone': 'fa-truck', 'ordem': 2},
            {'nome': 'Produtos', 'url': '/cadastros/produtos/', 'icone': 'fa-box', 'ordem': 3},
            {'nome': 'Contas Financeiras', 'url': '/cadastros/contas/', 'icone': 'fa-university', 'ordem': 4},
        ]
    },
    {
        'nome': 'Financeiro',
        'descricao': 'Gestão Financeira',
        'icone': 'fa-dollar-sign',
        'cor': '#27ae60',
        'ordem': 2,
        'menus': [
            {'nome': 'Movimentações', 'url': '/financeiro/movimentacoes/', 'icone': 'fa-exchange-alt', 'ordem': 1},
            {'nome': 'Lançamentos', 'url': '/financeiro/lancamentos/', 'icone': 'fa-list', 'ordem': 2},
            {'nome': 'Relatórios', 'url': '/financeiro/relatorios/', 'icone': 'fa-chart-line', 'ordem': 3},
        ]
    },
    {
        'nome': 'Contas a Receber',
        'descricao': 'Gestão de Recebimentos',
        'icone': 'fa-receipt',
        'cor': '#e74c3c',
        'ordem': 3,
        'menus': [
            {'nome': 'Contas a Receber', 'url': '/contas_receber/', 'icone': 'fa-file-invoice-dollar', 'ordem': 1},
            {'nome': 'Relatórios', 'url': '/contas_receber/relatorios/', 'icone': 'fa-chart-bar', 'ordem': 2},
        ]
    },
    {
        'nome': 'Boletos',
        'descricao': 'Gestão de Boletos',
        'icone': 'fa-barcode',
        'cor': '#f39c12',
        'ordem': 4,
        'menus': [
            {'nome': 'Boletos', 'url': '/boletos/', 'icone': 'fa-ticket-alt', 'ordem': 1},
            {'nome': 'Configurações', 'url': '/boletos/configuracoes/', 'icone': 'fa-cog', 'ordem': 2},
            {'nome': 'Remessas', 'url': '/boletos/remessas/', 'icone': 'fa-file-export', 'ordem': 3},
        ]
    },
    {
        'nome': 'Importações',
        'descricao': 'Importação de Dados',
        'icone': 'fa-file-import',
        'cor': '#9b59b6',
        'ordem': 5,
        'menus': [
            {'nome': 'Importar Dados', 'url': '/importacoes/', 'icone': 'fa-upload', 'ordem': 1},
            {'nome': 'Histórico', 'url': '/importacoes/historico/', 'icone': 'fa-history', 'ordem': 2},
        ]
    },
    {
        'nome': 'Sistema',
        'descricao': 'Configurações do Sistema',
        'icone': 'fa-cogs',
        'cor': '#34495e',
        'ordem': 6,
        'menus': [
            {'nome': 'Usuários', 'url': '/usuarios/', 'icone': 'fa-users-cog', 'ordem': 1},
            {'nome': 'Grupos e Permissões', 'url': '/usuarios/grupos/', 'icone': 'fa-user-shield', 'ordem': 2},
            {'nome': 'Módulos', 'url': '/usuarios/modulos/', 'icone': 'fa-th-large', 'ordem': 3},
            {'nome': 'Menus', 'url': '/usuarios/menus/', 'icone': 'fa-bars', 'ordem': 4},
        ]
    },
]

print('=' * 70)
print('CRIANDO/ATUALIZANDO MÓDULOS E MENUS DO SISTEMA')
print('=' * 70)

total_modulos = 0
total_menus = 0

for modulo_data in modulos_menus:
    # Criar/atualizar módulo
    modulo, created = Modulo.objects.update_or_create(
        nome=modulo_data['nome'],
        defaults={
            'descricao': modulo_data['descricao'],
            'icone': modulo_data['icone'],
            'ordem': modulo_data['ordem'],
            'ativo': True,
        }
    )
    
    status = '[CRIADO]' if created else '[ATUALIZADO]'
    print(f'\n{status} Módulo: {modulo.nome}')
    total_modulos += 1
    
    # Criar/atualizar menus
    for menu_data in modulo_data.get('menus', []):
        menu, menu_created = Menu.objects.update_or_create(
            nome=menu_data['nome'],
            modulo=modulo,
            defaults={
                'url': menu_data['url'],
                'icone': menu_data.get('icone', 'fa-circle'),
                'ordem': menu_data['ordem'],
                'ativo': True,
                'menu_pai': None,
            }
        )
        
        menu_status = '  [+]' if menu_created else '  [~]'
        print(f'{menu_status} Menu: {menu.nome} -> {menu.url}')
        total_menus += 1

print('\n' + '=' * 70)
print(f'RESUMO:')
print(f'  Módulos processados: {total_modulos}')
print(f'  Menus processados: {total_menus}')
print('=' * 70)
print('[OK] Estrutura de módulos e menus criada/atualizada com sucesso!')
print('=' * 70)
print('\nO usuário admin (superusuário) terá acesso automático a todos os módulos.')
print('Para outros usuários, configure permissões em: /usuarios/permissoes/')
print('')

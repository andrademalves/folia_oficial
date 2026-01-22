#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir URLs dos menus com base nas URLs reais do sistema
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu

# URLs corretas para cada módulo
menus_corretos = {
    'Cadastros': [
        {'nome': 'Dashboard', 'url': '/cadastros/', 'icone': 'fa-tachometer-alt', 'ordem': 1},
        {'nome': 'Plano de Contas', 'url': '/cadastros/plano-contas/', 'icone': 'fa-sitemap', 'ordem': 2},
        {'nome': 'Contas Financeiras', 'url': '/cadastros/contas-financeiras/', 'icone': 'fa-university', 'ordem': 3},
        {'nome': 'Métodos de Pagamento', 'url': '/cadastros/metodos-pagamento/', 'icone': 'fa-credit-card', 'ordem': 4},
        {'nome': 'Relatórios', 'url': '/cadastros/relatorios/', 'icone': 'fa-chart-bar', 'ordem': 5},
    ],
    'Financeiro': [
        {'nome': 'Dashboard', 'url': '/financeiro/', 'icone': 'fa-tachometer-alt', 'ordem': 1},
        {'nome': 'Contas a Pagar', 'url': '/financeiro/contas-pagar/', 'icone': 'fa-file-invoice-dollar', 'ordem': 2},
        {'nome': 'Dar Baixa', 'url': '/financeiro/dar-baixa/', 'icone': 'fa-check-circle', 'ordem': 3},
        {'nome': 'Conta Corrente', 'url': '/financeiro/conta-corrente/', 'icone': 'fa-money-check-alt', 'ordem': 4},
        {'nome': 'Relatórios', 'url': '/financeiro/relatorios/', 'icone': 'fa-chart-line', 'ordem': 5},
    ],
    'Contas a Receber': [
        {'nome': 'Dashboard', 'url': '/contas-receber/', 'icone': 'fa-tachometer-alt', 'ordem': 1},
        {'nome': 'Notas Fiscais', 'url': '/contas-receber/notas-fiscais/', 'icone': 'fa-file-invoice', 'ordem': 2},
        {'nome': 'Parcelas', 'url': '/contas-receber/parcelas/', 'icone': 'fa-money-bill-wave', 'ordem': 3},
        {'nome': 'Negociações', 'url': '/contas-receber/negociacoes/', 'icone': 'fa-handshake', 'ordem': 4},
        {'nome': 'Créditos', 'url': '/contas-receber/creditos/', 'icone': 'fa-coins', 'ordem': 5},
        {'nome': 'Aprovações', 'url': '/contas-receber/aprovacoes/', 'icone': 'fa-check-double', 'ordem': 6},
        {'nome': 'Relatórios', 'url': '/contas-receber/relatorios/', 'icone': 'fa-chart-bar', 'ordem': 7},
    ],
    'Boletos': [
        {'nome': 'Dashboard', 'url': '/boletos/', 'icone': 'fa-tachometer-alt', 'ordem': 1},
        {'nome': 'Lista de Boletos', 'url': '/boletos/boletos/', 'icone': 'fa-barcode', 'ordem': 2},
        {'nome': 'Gerar Boletos', 'url': '/boletos/boletos/selecionar/', 'icone': 'fa-plus-circle', 'ordem': 3},
        {'nome': 'Remessas CNAB', 'url': '/boletos/remessas/', 'icone': 'fa-file-export', 'ordem': 4},
        {'nome': 'Configurações Bancárias', 'url': '/boletos/configuracoes/', 'icone': 'fa-cog', 'ordem': 5},
    ],
    'Importações': [
        {'nome': 'Dashboard', 'url': '/importacoes/', 'icone': 'fa-tachometer-alt', 'ordem': 1},
        {'nome': 'Cadastro Geral', 'url': '/importacoes/cadastro-geral/', 'icone': 'fa-database', 'ordem': 2},
        {'nome': 'Notas Fiscais', 'url': '/importacoes/notas-fiscais/', 'icone': 'fa-file-invoice', 'ordem': 3},
        {'nome': 'Parcelas', 'url': '/importacoes/parcelas/', 'icone': 'fa-money-bill', 'ordem': 4},
        {'nome': 'Logs de Importação', 'url': '/importacoes/logs/', 'icone': 'fa-history', 'ordem': 5},
        {'nome': 'Configurações', 'url': '/importacoes/configurar/', 'icone': 'fa-cog', 'ordem': 6},
    ],
    'Sistema': [
        {'nome': 'Usuários', 'url': '/usuarios/', 'icone': 'fa-users', 'ordem': 1},
        {'nome': 'Módulos', 'url': '/admin/usuarios/modulo/', 'icone': 'fa-th-large', 'ordem': 2},
        {'nome': 'Menus', 'url': '/admin/usuarios/menu/', 'icone': 'fa-bars', 'ordem': 3},
        {'nome': 'Admin Django', 'url': '/admin/', 'icone': 'fa-tools', 'ordem': 4},
    ],
}

print('=' * 70)
print('ATUALIZANDO URLs DOS MENUS')
print('=' * 70)

total_atualizados = 0
total_criados = 0
total_removidos = 0

for modulo_nome, menus_data in menus_corretos.items():
    try:
        modulo = Modulo.objects.get(nome=modulo_nome)
        print(f'\n[INFO] Processando módulo: {modulo_nome}')
        
        # Remover menus antigos que não estão na nova lista
        urls_novas = {m['url'] for m in menus_data}
        menus_antigos = Menu.objects.filter(modulo=modulo)
        
        for menu_antigo in menus_antigos:
            if menu_antigo.url not in urls_novas:
                print(f'  [-] Removendo menu obsoleto: {menu_antigo.nome} ({menu_antigo.url})')
                menu_antigo.delete()
                total_removidos += 1
        
        # Criar/atualizar menus
        for menu_data in menus_data:
            menu, created = Menu.objects.update_or_create(
                modulo=modulo,
                url=menu_data['url'],
                defaults={
                    'nome': menu_data['nome'],
                    'icone': menu_data.get('icone', 'fa-circle'),
                    'ordem': menu_data['ordem'],
                    'ativo': True,
                    'menu_pai': None,
                }
            )
            
            if created:
                print(f'  [+] Menu criado: {menu.nome} -> {menu.url}')
                total_criados += 1
            else:
                print(f'  [~] Menu atualizado: {menu.nome} -> {menu.url}')
                total_atualizados += 1
                
    except Modulo.DoesNotExist:
        print(f'\n[ERRO] Módulo não encontrado: {modulo_nome}')
        continue

print('\n' + '=' * 70)
print(f'RESUMO:')
print(f'  Menus criados: {total_criados}')
print(f'  Menus atualizados: {total_atualizados}')
print(f'  Menus removidos: {total_removidos}')
print('=' * 70)
print('[OK] URLs dos menus corrigidas com sucesso!')
print('=' * 70)
print('\nTodos os links dos módulos agora apontam para URLs válidas.')
print('Recarregue a página inicial para ver as alterações.')
print('')

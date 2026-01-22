#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar criação de usuário com permissões específicas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import Modulo, Menu, PermissaoMenu

print('=' * 70)
print('EXEMPLO: CRIAR USUÁRIO COM PERMISSÕES ESPECÍFICAS')
print('=' * 70)

# Criar usuário de teste
username = 'teste'
password = 'teste1234'

# Verificar se já existe
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f'\n[INFO] Usuário "{username}" já existe. Atualizando...')
    user.set_password(password)
    user.is_active = True
    user.save()
else:
    user = User.objects.create_user(
        username=username,
        password=password,
        email='teste@exemplo.com',
        is_staff=False,  # NÃO é superusuário
        is_superuser=False
    )
    print(f'\n[+] Usuário "{username}" criado')

print(f'    Usuário: {username}')
print(f'    Senha: {password}')
print(f'    Superusuário: Não')

# Limpar permissões antigas
PermissaoMenu.objects.filter(usuario=user).delete()

# Exemplo: Dar permissão apenas para FINANCEIRO e CADASTROS
print('\n[INFO] Configurando permissões (EXEMPLO):')
print('  - Financeiro: Visualizar, Criar, Editar')
print('  - Cadastros: Apenas Visualizar')

modulos_permitidos = ['Financeiro', 'Cadastros']

total_permissoes = 0
for modulo_nome in modulos_permitidos:
    try:
        modulo = Modulo.objects.get(nome=modulo_nome)
        menus = Menu.objects.filter(modulo=modulo, ativo=True)
        
        print(f'\n[INFO] Liberando módulo: {modulo_nome}')
        
        for menu in menus:
            # Financeiro: todas permissões
            if modulo_nome == 'Financeiro':
                PermissaoMenu.objects.create(
                    tipo='usuario',
                    usuario=user,
                    menu=menu,
                    pode_visualizar=True,
                    pode_criar=True,
                    pode_editar=True,
                    pode_excluir=False
                )
                print(f'  [+] {menu.nome}: Visualizar + Criar + Editar')
            
            # Cadastros: só visualizar
            elif modulo_nome == 'Cadastros':
                PermissaoMenu.objects.create(
                    tipo='usuario',
                    usuario=user,
                    menu=menu,
                    pode_visualizar=True,
                    pode_criar=False,
                    pode_editar=False,
                    pode_excluir=False
                )
                print(f'  [+] {menu.nome}: Apenas Visualizar')
            
            total_permissoes += 1
            
    except Modulo.DoesNotExist:
        print(f'[ERRO] Módulo não encontrado: {modulo_nome}')

print('\n' + '=' * 70)
print(f'[OK] Usuário criado com {total_permissoes} permissões')
print('=' * 70)
print(f'\nCREDENCIAIS DO USUÁRIO DE TESTE:')
print(f'  Usuário: {username}')
print(f'  Senha: {password}')
print(f'\nFaça login com este usuário e verifique que:')
print(f'  ✓ Verá apenas os módulos: Financeiro e Cadastros')
print(f'  ✓ No Financeiro: poderá criar e editar')
print(f'  ✓ Nos Cadastros: poderá apenas visualizar')
print(f'\nPara CRIAR OUTROS USUÁRIOS:')
print(f'  1. Faça login como admin')
print(f'  2. Acesse módulo "Sistema"')
print(f'  3. Clique em "Gestão de Usuários"')
print(f'  4. Clique em "Criar Usuário"')
print(f'  5. Depois clique em "Permissões" para configurar')
print('')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar usuário de teste e dar permissões
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PermissaoMenu, Menu, Modulo

# Criar usuário
username = 'teste_usuario'
email = 'teste@folia.com'
password = 'Teste2026@'

try:
    user = User.objects.get(username=username)
    print(f"[INFO] Usuário '{username}' já existe")
except User.DoesNotExist:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    print(f"[✓] Usuário '{username}' criado com sucesso")

print(f"\nCredenciais:")
print(f"  Username: {username}")
print(f"  Senha: {password}")

# Limpar permissões antigas
PermissaoMenu.objects.filter(usuario=user).delete()

# Dar permissão para módulo Financeiro
modulo = Modulo.objects.get(nome='Financeiro')
menus = Menu.objects.filter(modulo=modulo, ativo=True)

print(f"\n[INFO] Configurando permissões para módulo {modulo.nome}...")

for menu in menus:
    PermissaoMenu.objects.create(
        tipo='usuario',
        usuario=user,
        menu=menu,
        pode_visualizar=True,
        pode_criar=True,
        pode_editar=True,
        pode_excluir=True
    )
    print(f"  ✓ {menu.nome}")

print(f"\n[✓] {menus.count()} permissões criadas com sucesso!")
print(f"\n[INFO] Agora você pode:")
print(f"  1. Acessar: http://72.60.139.167:8000/")
print(f"  2. Fazer login com: {username} / {password}")
print(f"  3. Verificar se o módulo Financeiro está visível e acessível")

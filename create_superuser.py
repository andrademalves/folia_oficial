#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar superusuário admin
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Dados do superusuário
username = 'admin'
email = 'admin@gestao.local'
password = 'adm1234@'

# Verificar se usuário já existe
if User.objects.filter(username=username).exists():
    print(f'[INFO] Usuário "{username}" já existe. Atualizando senha...')
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()
    print(f'[OK] Senha do usuário "{username}" atualizada!')
else:
    print(f'[INFO] Criando superusuário "{username}"...')
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'[OK] Superusuário "{username}" criado com sucesso!')

print(f'\n=== CREDENCIAIS DE ACESSO ===')
print(f'Usuário: {username}')
print(f'Senha: {password}')
print(f'Email: {email}')
print(f'Superusuário: Sim')
print(f'Acesso Admin: Sim')
print(f'=============================\n')

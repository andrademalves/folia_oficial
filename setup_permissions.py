#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar permissões completas do superusuário admin
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

# Buscar usuário admin
try:
    admin_user = User.objects.get(username='admin')
    print(f'[INFO] Usuário "admin" encontrado')
except User.DoesNotExist:
    print('[ERRO] Usuário "admin" não encontrado!')
    exit(1)

# Garantir que é superusuário
admin_user.is_superuser = True
admin_user.is_staff = True
admin_user.is_active = True
admin_user.save()
print(f'[OK] Status de superusuário confirmado')

# Listar todos os apps do sistema
apps_do_sistema = [
    'boletos',
    'cadastros',
    'contas_receber',
    'financeiro',
    'importacoes',
    'usuarios',
]

print(f'\n[INFO] Configurando permissões para {len(apps_do_sistema)} módulos...\n')

# Criar/atualizar grupos de permissão para cada módulo
grupos_criados = []

for app_name in apps_do_sistema:
    # Criar grupo para o módulo
    group_name = f'Acesso_{app_name.title()}'
    group, created = Group.objects.get_or_create(name=group_name)
    
    if created:
        print(f'[+] Grupo criado: {group_name}')
    else:
        print(f'[~] Grupo existente: {group_name}')
    
    # Buscar todas as permissões do app
    permissions = Permission.objects.filter(
        content_type__app_label=app_name
    )
    
    # Adicionar todas as permissões ao grupo
    for perm in permissions:
        group.permissions.add(perm)
    
    print(f'    └─ {permissions.count()} permissões adicionadas')
    
    # Adicionar admin ao grupo
    admin_user.groups.add(group)
    grupos_criados.append(group_name)

# Adicionar permissões dos apps padrão do Django
django_apps = ['admin', 'auth', 'contenttypes', 'sessions']
for app_name in django_apps:
    permissions = Permission.objects.filter(
        content_type__app_label=app_name
    )
    for perm in permissions:
        admin_user.user_permissions.add(perm)

print(f'\n[OK] Usuário "admin" adicionado a {len(grupos_criados)} grupos')

# Resumo final
print(f'\n{"=" * 60}')
print(f'RESUMO DE PERMISSÕES - USUÁRIO: admin')
print(f'{"=" * 60}')
print(f'Superusuário: {"SIM" if admin_user.is_superuser else "NÃO"}')
print(f'Staff (Admin Django): {"SIM" if admin_user.is_staff else "NÃO"}')
print(f'Ativo: {"SIM" if admin_user.is_active else "NÃO"}')
print(f'\nGrupos de Acesso ({admin_user.groups.count()}):')
for grupo in admin_user.groups.all():
    print(f'  ✓ {grupo.name}')

print(f'\nMódulos com Acesso Completo:')
for app in apps_do_sistema:
    print(f'  ✓ {app.title()}')

print(f'\n{"=" * 60}')
print(f'[OK] Configuração concluída com sucesso!')
print(f'{"=" * 60}\n')

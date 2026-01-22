#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas de permissões
Verifica todos os aspectos do sistema de permissões
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PermissaoMenu, Menu, Modulo

print("=" * 80)
print("DIAGNÓSTICO COMPLETO DO SISTEMA DE PERMISSÕES")
print("=" * 80)

# Pedir usuário para diagnóstico
username = input("\nDigite o username do usuário para diagnosticar (ou Enter para listar todos): ").strip()

if username:
    try:
        user = User.objects.get(username=username)
        usuarios = [user]
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")
        exit(1)
else:
    # Lista todos os usuários não-superusuários
    usuarios = User.objects.filter(is_superuser=False, is_active=True)
    print(f"\n[INFO] Diagnosticando {usuarios.count()} usuários ativos\n")

for user in usuarios:
    print("\n" + "=" * 80)
    print(f"USUÁRIO: {user.username}")
    print("=" * 80)
    
    # 1. Verificar se é superusuário
    print(f"\n1. Status do Usuário:")
    print(f"   - Superusuário: {'SIM' if user.is_superuser else 'NÃO'}")
    print(f"   - Ativo: {'SIM' if user.is_active else 'NÃO'}")
    print(f"   - Staff: {'SIM' if user.is_staff else 'NÃO'}")
    
    # 2. Verificar grupos
    grupos = user.groups.all()
    print(f"\n2. Grupos ({grupos.count()}):")
    if grupos.exists():
        for grupo in grupos:
            print(f"   - {grupo.name}")
    else:
        print("   - Nenhum grupo atribuído")
    
    # 3. Verificar permissões diretas do usuário
    permissoes_usuario = PermissaoMenu.objects.filter(usuario=user).select_related('menu', 'menu__modulo')
    print(f"\n3. Permissões Diretas ({permissoes_usuario.count()}):")
    
    problemas_usuario = []
    for perm in permissoes_usuario:
        status = "✓"
        detalhes = []
        
        # Verifica campo tipo
        if not perm.tipo or perm.tipo == '':
            status = "✗"
            detalhes.append("TIPO VAZIO")
            problemas_usuario.append(f"Menu '{perm.menu.nome}' sem campo tipo")
        elif perm.tipo != 'usuario':
            status = "✗"
            detalhes.append(f"TIPO ERRADO: {perm.tipo}")
            problemas_usuario.append(f"Menu '{perm.menu.nome}' com tipo='{perm.tipo}' mas deveria ser 'usuario'")
        
        # Verifica se menu está ativo
        if not perm.menu.ativo:
            status = "⚠"
            detalhes.append("MENU INATIVO")
        
        # Verifica se módulo está ativo
        if not perm.menu.modulo.ativo:
            status = "⚠"
            detalhes.append("MÓDULO INATIVO")
        
        perms_str = []
        if perm.pode_visualizar: perms_str.append("V")
        if perm.pode_criar: perms_str.append("C")
        if perm.pode_editar: perms_str.append("E")
        if perm.pode_excluir: perms_str.append("X")
        
        info = f" [{','.join(perms_str)}]" if perms_str else " [SEM PERMISSÕES]"
        
        if detalhes:
            print(f"   {status} {perm.menu.modulo.nome} > {perm.menu.nome}{info} - {', '.join(detalhes)}")
        else:
            print(f"   {status} {perm.menu.modulo.nome} > {perm.menu.nome}{info}")
    
    if not permissoes_usuario.exists():
        print("   - Nenhuma permissão direta")
    
    # 4. Verificar permissões por grupo
    if grupos.exists():
        permissoes_grupo = PermissaoMenu.objects.filter(grupo__in=grupos).select_related('menu', 'menu__modulo', 'grupo')
        print(f"\n4. Permissões por Grupo ({permissoes_grupo.count()}):")
        
        problemas_grupo = []
        for perm in permissoes_grupo:
            status = "✓"
            detalhes = []
            
            # Verifica campo tipo
            if not perm.tipo or perm.tipo == '':
                status = "✗"
                detalhes.append("TIPO VAZIO")
                problemas_grupo.append(f"Menu '{perm.menu.nome}' do grupo '{perm.grupo.name}' sem campo tipo")
            elif perm.tipo != 'grupo':
                status = "✗"
                detalhes.append(f"TIPO ERRADO: {perm.tipo}")
                problemas_grupo.append(f"Menu '{perm.menu.nome}' do grupo '{perm.grupo.name}' com tipo='{perm.tipo}' mas deveria ser 'grupo'")
            
            # Verifica se menu está ativo
            if not perm.menu.ativo:
                status = "⚠"
                detalhes.append("MENU INATIVO")
            
            # Verifica se módulo está ativo
            if not perm.menu.modulo.ativo:
                status = "⚠"
                detalhes.append("MÓDULO INATIVO")
            
            perms_str = []
            if perm.pode_visualizar: perms_str.append("V")
            if perm.pode_criar: perms_str.append("C")
            if perm.pode_editar: perms_str.append("E")
            if perm.pode_excluir: perms_str.append("X")
            
            info = f" [{','.join(perms_str)}]" if perms_str else " [SEM PERMISSÕES]"
            
            if detalhes:
                print(f"   {status} [{perm.grupo.name}] {perm.menu.modulo.nome} > {perm.menu.nome}{info} - {', '.join(detalhes)}")
            else:
                print(f"   {status} [{perm.grupo.name}] {perm.menu.modulo.nome} > {perm.menu.nome}{info}")
    else:
        print(f"\n4. Permissões por Grupo:")
        print("   - Usuário não pertence a nenhum grupo")
        problemas_grupo = []
    
    # 5. Módulos que o usuário deveria ver
    menus_visiveis_usuario = PermissaoMenu.objects.filter(
        usuario=user,
        pode_visualizar=True,
        menu__ativo=True,
        menu__modulo__ativo=True
    ).values_list('menu__modulo__nome', flat=True).distinct()
    
    menus_visiveis_grupo = []
    if grupos.exists():
        menus_visiveis_grupo = PermissaoMenu.objects.filter(
            grupo__in=grupos,
            pode_visualizar=True,
            menu__ativo=True,
            menu__modulo__ativo=True
        ).values_list('menu__modulo__nome', flat=True).distinct()
    
    modulos_visiveis = set(list(menus_visiveis_usuario) + list(menus_visiveis_grupo))
    
    print(f"\n5. Módulos Visíveis ({len(modulos_visiveis)}):")
    if modulos_visiveis:
        for modulo in sorted(modulos_visiveis):
            print(f"   ✓ {modulo}")
    else:
        print("   ❌ NENHUM MÓDULO VISÍVEL - USUÁRIO NÃO VERÁ NADA!")
    
    # 6. Resumo de problemas
    print(f"\n6. Problemas Encontrados:")
    todos_problemas = problemas_usuario + problemas_grupo
    if todos_problemas:
        print(f"   ⚠️ {len(todos_problemas)} problema(s) encontrado(s):")
        for problema in todos_problemas:
            print(f"      - {problema}")
        print(f"\n   💡 Execute o script 'corrigir_permissoes_tipo.py' para corrigir!")
    else:
        print("   ✅ Nenhum problema encontrado!")

print("\n" + "=" * 80)
print("DIAGNÓSTICO CONCLUÍDO")
print("=" * 80)
print("\nLegenda:")
print("  ✓ = OK")
print("  ✗ = ERRO (precisa correção)")
print("  ⚠ = AVISO (pode afetar funcionamento)")
print("  V = Pode Visualizar")
print("  C = Pode Criar")
print("  E = Pode Editar")
print("  X = Pode Excluir")
print("\n" + "=" * 80)

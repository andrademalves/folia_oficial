#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de instalação e correção completa para servidor de produção
Corrige todos os problemas conhecidos de permissões
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PermissaoMenu, Menu, Modulo

print("=" * 80)
print("INSTALAÇÃO E CORREÇÃO COMPLETA - SERVIDOR DE PRODUÇÃO")
print("=" * 80)

# ETAPA 1: Corrigir campo 'tipo' em todas as permissões
print("\n[ETAPA 1/3] Corrigindo campo 'tipo' nas permissões...")
print("-" * 80)

todas_permissoes = PermissaoMenu.objects.all()
total = todas_permissoes.count()

print(f"Total de permissões: {total}")

corrigidas_tipo = 0
erros_tipo = 0

for permissao in todas_permissoes:
    try:
        tipo_original = permissao.tipo
        
        # Corrige tipo vazio ou None
        if not tipo_original or tipo_original == '':
            if permissao.usuario is not None:
                permissao.tipo = 'usuario'
                permissao.save()
                print(f"  ✓ {permissao.menu.nome} -> tipo='usuario' (era vazio)")
                corrigidas_tipo += 1
            elif permissao.grupo is not None:
                permissao.tipo = 'grupo'
                permissao.save()
                print(f"  ✓ {permissao.menu.nome} -> tipo='grupo' (era vazio)")
                corrigidas_tipo += 1
            else:
                print(f"  ✗ ERRO: Permissão sem usuário nem grupo - Menu: {permissao.menu.nome}")
                erros_tipo += 1
        
        # Corrige tipo inconsistente
        elif tipo_original == 'usuario' and permissao.usuario is None and permissao.grupo is not None:
            permissao.tipo = 'grupo'
            permissao.save()
            print(f"  ✓ {permissao.menu.nome} -> tipo corrigido de 'usuario' para 'grupo'")
            corrigidas_tipo += 1
        
        elif tipo_original == 'grupo' and permissao.grupo is None and permissao.usuario is not None:
            permissao.tipo = 'usuario'
            permissao.save()
            print(f"  ✓ {permissao.menu.nome} -> tipo corrigido de 'grupo' para 'usuario'")
            corrigidas_tipo += 1
            
    except Exception as e:
        print(f"  ✗ ERRO ao processar permissão {permissao.id}: {str(e)}")
        erros_tipo += 1

print(f"\nResultado Etapa 1:")
print(f"  - Corrigidas: {corrigidas_tipo}")
print(f"  - Erros: {erros_tipo}")

# ETAPA 2: Garantir que todos os usuários não-superusuários têm o campo tipo correto
print("\n[ETAPA 2/3] Verificando consistência de permissões por usuário...")
print("-" * 80)

usuarios = User.objects.filter(is_superuser=False, is_active=True)
print(f"Verificando {usuarios.count()} usuários ativos...")

usuarios_corrigidos = 0

for user in usuarios:
    # Verificar permissões do usuário
    perms_usuario = PermissaoMenu.objects.filter(usuario=user)
    
    if perms_usuario.exists():
        problemas_usuario = perms_usuario.exclude(tipo='usuario').count()
        
        if problemas_usuario > 0:
            # Corrige todas as permissões deste usuário
            perms_usuario.update(tipo='usuario')
            print(f"  ✓ {user.username}: {problemas_usuario} permissões corrigidas")
            usuarios_corrigidos += 1

print(f"\nResultado Etapa 2:")
print(f"  - Usuários corrigidos: {usuarios_corrigidos}")

# ETAPA 3: Garantir que todos os grupos têm o campo tipo correto
print("\n[ETAPA 3/3] Verificando consistência de permissões por grupo...")
print("-" * 80)

from django.contrib.auth.models import Group

grupos = Group.objects.all()
print(f"Verificando {grupos.count()} grupos...")

grupos_corrigidos = 0

for grupo in grupos:
    # Verificar permissões do grupo
    perms_grupo = PermissaoMenu.objects.filter(grupo=grupo)
    
    if perms_grupo.exists():
        problemas_grupo = perms_grupo.exclude(tipo='grupo').count()
        
        if problemas_grupo > 0:
            # Corrige todas as permissões deste grupo
            perms_grupo.update(tipo='grupo')
            print(f"  ✓ {grupo.name}: {problemas_grupo} permissões corrigidas")
            grupos_corrigidos += 1

print(f"\nResultado Etapa 3:")
print(f"  - Grupos corrigidos: {grupos_corrigidos}")

# RESUMO FINAL
print("\n" + "=" * 80)
print("RESUMO FINAL DA CORREÇÃO")
print("=" * 80)
print(f"Total de permissões: {total}")
print(f"Permissões corrigidas: {corrigidas_tipo}")
print(f"Usuários corrigidos: {usuarios_corrigidos}")
print(f"Grupos corrigidos: {grupos_corrigidos}")
print(f"Erros: {erros_tipo}")

if corrigidas_tipo > 0 or usuarios_corrigidos > 0 or grupos_corrigidos > 0:
    print("\n✅ CORREÇÕES APLICADAS COM SUCESSO!")
    print("   Os usuários agora devem ter acesso aos menus conforme permissões.")
elif erros_tipo > 0:
    print("\n⚠️ ATENÇÃO: Foram encontrados erros!")
    print("   Verifique as permissões com erro acima.")
else:
    print("\n✅ SISTEMA JÁ ESTAVA CORRETO!")
    print("   Nenhuma correção foi necessária.")

print("\n" + "=" * 80)
print("PRÓXIMOS PASSOS:")
print("=" * 80)
print("1. Reinicie o servidor Django:")
print("   python manage.py runserver 0.0.0.0:8000")
print("\n2. Faça logout e login novamente com o usuário")
print("\n3. Verifique se os módulos estão visíveis e acessíveis")
print("\n" + "=" * 80)

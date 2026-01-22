#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir o campo 'tipo' nas permissões de menu
Este script resolve o problema de "Menu não encontrado" quando permissões são criadas pelo painel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import PermissaoMenu

print("=" * 80)
print("CORREÇÃO DE PERMISSÕES - CAMPO TIPO")
print("=" * 80)

# Buscar todas as permissões
todas_permissoes = PermissaoMenu.objects.all()
total = todas_permissoes.count()

print(f"\n[INFO] Total de permissões encontradas: {total}")

if total == 0:
    print("[AVISO] Nenhuma permissão encontrada no sistema")
    exit(0)

# Contadores
corrigidas = 0
ja_corretas = 0
erros = 0

print("\n[PROCESSANDO] Analisando permissões...\n")

for permissao in todas_permissoes:
    try:
        # Verifica se tem tipo definido
        tipo_atual = permissao.tipo
        
        # Se tipo está None ou vazio, corrige baseado nos campos preenchidos
        if not tipo_atual or tipo_atual == '':
            if permissao.usuario is not None:
                permissao.tipo = 'usuario'
                permissao.save()
                print(f"  ✓ Corrigida: {permissao.menu.nome} -> tipo='usuario' para {permissao.usuario.username}")
                corrigidas += 1
            elif permissao.grupo is not None:
                permissao.tipo = 'grupo'
                permissao.save()
                print(f"  ✓ Corrigida: {permissao.menu.nome} -> tipo='grupo' para {permissao.grupo.name}")
                corrigidas += 1
            else:
                print(f"  ✗ ERRO: Permissão sem usuário nem grupo - Menu: {permissao.menu.nome}")
                erros += 1
        
        # Se tipo está definido mas inconsistente com os dados
        elif tipo_atual == 'usuario' and permissao.usuario is None:
            if permissao.grupo is not None:
                permissao.tipo = 'grupo'
                permissao.save()
                print(f"  ✓ Corrigida: {permissao.menu.nome} -> tipo mudado de 'usuario' para 'grupo'")
                corrigidas += 1
            else:
                print(f"  ✗ ERRO: Permissão tipo='usuario' mas sem usuário - Menu: {permissao.menu.nome}")
                erros += 1
        
        elif tipo_atual == 'grupo' and permissao.grupo is None:
            if permissao.usuario is not None:
                permissao.tipo = 'usuario'
                permissao.save()
                print(f"  ✓ Corrigida: {permissao.menu.nome} -> tipo mudado de 'grupo' para 'usuario'")
                corrigidas += 1
            else:
                print(f"  ✗ ERRO: Permissão tipo='grupo' mas sem grupo - Menu: {permissao.menu.nome}")
                erros += 1
        
        else:
            # Permissão já está correta
            ja_corretas += 1
    
    except Exception as e:
        print(f"  ✗ ERRO ao processar permissão {permissao.id}: {str(e)}")
        erros += 1

# Resumo
print("\n" + "=" * 80)
print("RESUMO DA CORREÇÃO")
print("=" * 80)
print(f"Total de permissões: {total}")
print(f"Já corretas: {ja_corretas}")
print(f"Corrigidas: {corrigidas}")
print(f"Erros: {erros}")

if corrigidas > 0:
    print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("As permissões foram corrigidas. Os usuários agora devem ter acesso aos menus.")
elif erros > 0:
    print("\n⚠️ ATENÇÃO: Foram encontrados erros!")
    print("Verifique as permissões com erro acima.")
else:
    print("\n✅ TODAS AS PERMISSÕES JÁ ESTAVAM CORRETAS!")

print("\n" + "=" * 80)

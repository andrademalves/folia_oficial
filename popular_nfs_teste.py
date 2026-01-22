#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from contas_receber.models import NotaFiscal, Cliente
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User

def popular_dados_teste():
    # Buscar ou criar usuário
    user = User.objects.first()
    if not user:
        print("❌ Nenhum usuário encontrado. Crie um usuário primeiro!")
        return
    
    print(f"✓ Usuário encontrado: {user.username}")
    
    # Verificar se já existem dados
    if Cliente.objects.exists():
        print(f"⚠ Já existem {Cliente.objects.count()} clientes cadastrados")
        # Continuar mesmo assim para criar as NFs
    
    # Criar clientes
    print("\n📋 Criando clientes de teste...")
    
    cliente1, created = Cliente.objects.get_or_create(
        cpf_cnpj="12.345.678/0001-90",
        defaults={
            'nome': "Empresa Teste Ltda",
            'email': "teste1@email.com",
            'telefone': "(11) 98765-4321",
            'ativo': True
        }
    )
    if created:
        print(f"  ✓ Cliente criado: {cliente1.nome}")
    else:
        print(f"  ⚠ Cliente já existe: {cliente1.nome}")
    
    cliente2, created = Cliente.objects.get_or_create(
        cpf_cnpj="123.456.789-00",
        defaults={
            'nome': "João da Silva",
            'email': "joao@email.com",
            'telefone': "(11) 91234-5678",
            'ativo': True
        }
    )
    if created:
        print(f"  ✓ Cliente criado: {cliente2.nome}")
    else:
        print(f"  ⚠ Cliente já existe: {cliente2.nome}")
    
    cliente3, created = Cliente.objects.get_or_create(
        cpf_cnpj="987.654.321-00",
        defaults={
            'nome': "Maria Oliveira",
            'email': "maria@email.com",
            'telefone': "(11) 95555-4444",
            'ativo': True
        }
    )
    if created:
        print(f"  ✓ Cliente criado: {cliente3.nome}")
    else:
        print(f"  ⚠ Cliente já existe: {cliente3.nome}")
    
    # Criar notas fiscais
    print("\n📄 Criando notas fiscais de teste...")
    
    notas_dados = [
        {
            'cliente': cliente1,
            'numero_nota': '1001',
            'data_emissao': date(2025, 12, 1),
            'total_produto': Decimal('10000.00'),
            'total_ipi_valor': Decimal('500.00'),
            'total_nota': Decimal('1200.00'),
        },
        {
            'cliente': cliente1,
            'numero_nota': '1002',
            'data_emissao': date(2025, 12, 10),
            'total_produto': Decimal('5000.00'),
            'total_ipi_valor': Decimal('250.00'),
            'total_nota': Decimal('600.00'),
        },
        {
            'cliente': cliente2,
            'numero_nota': '1003',
            'data_emissao': date(2025, 12, 15),
            'total_produto': Decimal('8000.00'),
            'total_ipi_valor': Decimal('400.00'),
            'total_nota': Decimal('900.00'),
        },
        {
            'cliente': cliente2,
            'numero_nota': '1004',
            'data_emissao': date(2025, 12, 20),
            'total_produto': Decimal('15000.00'),
            'total_ipi_valor': Decimal('750.00'),
            'total_nota': Decimal('1800.00'),
        },
        {
            'cliente': cliente3,
            'numero_nota': '1005',
            'data_emissao': date(2025, 12, 22),
            'total_produto': Decimal('3000.00'),
            'total_ipi_valor': Decimal('150.00'),
            'total_nota': Decimal('350.00'),
        },
        {
            'cliente': cliente3,
            'numero_nota': '2001',
            'data_emissao': date(2025, 11, 25),
            'total_produto': Decimal('12000.00'),
            'total_ipi_valor': Decimal('600.00'),
            'total_nota': Decimal('1400.00'),
        },
    ]
    
    for dados in notas_dados:
        nf, created = NotaFiscal.objects.get_or_create(
            numero_nota=dados['numero_nota'],
            defaults={
                'cliente': dados['cliente'],
                'data_emissao': dados['data_emissao'],
                'total_produto': dados['total_produto'],
                'total_ipi_valor': dados['total_ipi_valor'],
                'total_nota': dados['total_nota'],
            }
        )
        
        if created:
            valor_carteira = (dados['total_produto'] - dados['total_ipi_valor'])
            total_nf = valor_carteira + dados['total_nota']
            print(f"  ✓ NF {nf.numero_nota} - {nf.cliente.nome} - Carteira: R$ {valor_carteira:.2f} - Total: R$ {total_nf:.2f}")
        else:
            print(f"  ⚠ NF {nf.numero_nota} já existe")
    
    # Resumo
    print("\n" + "="*60)
    print(f"✅ Total de Clientes: {Cliente.objects.count()}")
    print(f"✅ Total de Notas Fiscais: {NotaFiscal.objects.count()}")
    print("="*60)
    
    print("\n📊 Resumo das Notas Fiscais:")
    for nf in NotaFiscal.objects.all().order_by('-data_emissao'):
        valor_carteira = nf.valor_carteira()
        total_nf = nf.valor_total_nf()
        print(f"  NF {nf.numero_nota} | {nf.data_emissao} | {nf.cliente.nome[:30]:30} | Carteira: R$ {valor_carteira:10,.2f} | Total: R$ {total_nf:10,.2f}")
    
    print("\n✅ Dados de teste criados com sucesso!")
    print(f"\n🌐 Acesse: http://127.0.0.1:8000/contas-receber/notas-fiscais/")

if __name__ == '__main__':
    popular_dados_teste()

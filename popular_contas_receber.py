import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from contas_receber.models import Cliente, OrigemCobranca, NotaFiscal, Parcela

print("🚀 Criando dados de teste para Contas a Receber...")

# Criar Origens
origens = []
for nome in ['Nota Fiscal', 'Carteira', 'Boleto', 'Pix']:
    origem, created = OrigemCobranca.objects.get_or_create(
        nome=nome,
        defaults={'descricao': f'Origem: {nome}', 'ativo': True}
    )
    origens.append(origem)
    if created:
        print(f"✅ Origem criada: {nome}")

# Criar Clientes
clientes = []
clientes_data = [
    {'nome': 'Empresa ABC Ltda', 'cpf_cnpj': '12.345.678/0001-90', 'email': 'contato@abc.com', 'telefone': '(11) 98765-4321'},
    {'nome': 'João Silva ME', 'cpf_cnpj': '98.765.432/0001-10', 'email': 'joao@silva.com', 'telefone': '(21) 99999-8888'},
    {'nome': 'Maria Santos', 'cpf_cnpj': '123.456.789-00', 'email': 'maria@email.com', 'telefone': '(31) 97777-6666'},
]

for dados in clientes_data:
    cliente, created = Cliente.objects.get_or_create(
        cpf_cnpj=dados['cpf_cnpj'],
        defaults=dados
    )
    clientes.append(cliente)
    if created:
        print(f"✅ Cliente criado: {dados['nome']}")

# Criar Notas Fiscais
notas_fiscais = []
for i in range(1, 6):
    nf, created = NotaFiscal.objects.get_or_create(
        numero_nota=f"{8000 + i}",
        serie="1",
        defaults={
            'cliente': clientes[i % len(clientes)],
            'numero_pedido': f"{139870 + i}",  # Número do pedido
            'data_emissao': datetime.now() - timedelta(days=i*10),
            'valor_produtos': Decimal(f"{1000 + i*500}.00"),
            'valor_ipi': Decimal(f"{100 + i*50}.00"),
            'valor_total': Decimal(f"{1100 + i*550}.00"),
            'ativo': True
        }
    )
    notas_fiscais.append(nf)
    if created:
        print(f"✅ Nota Fiscal criada: {nf.numero_nota}")

# Criar Parcelas
for nf in notas_fiscais:
    for parcela_num in range(1, 4):  # 3 parcelas por NF
        codigo = f"NF-{nf.numero_nota}-P{str(parcela_num).zfill(2)}"
        parcela, created = Parcela.objects.get_or_create(
            codigo_identificador=codigo,
            defaults={
                'nota_fiscal': nf,
                'cliente': nf.cliente,
                'origem': origens[0],
                'tipo_parcela': 'NF',
                'numero_parcela': parcela_num,
                'valor': nf.valor_total / 3,
                'data_vencimento': datetime.now().date() + timedelta(days=30*parcela_num),
                'status_pagamento': 'pendente'
            }
        )
        if created:
            print(f"✅ Parcela criada: {codigo}")

print("\n✨ Dados de teste criados com sucesso!")
print(f"📊 Total: {Cliente.objects.count()} clientes, {NotaFiscal.objects.count()} notas fiscais, {Parcela.objects.count()} parcelas")

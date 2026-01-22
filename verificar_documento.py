import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from importacoes.models import ContaParcelaFutura, NotaFiscalFutura

print("=== Verificando campo 'documento' das parcelas ===\n")

# Buscar algumas parcelas
parcelas = ContaParcelaFutura.objects.all()[:10]

for p in parcelas:
    print(f"ID: {p.id}")
    print(f"Documento: {p.documento}")
    print(f"FK_NF: {p.fk_nota_fiscal}")
    print(f"Vencimento: {p.data_vencimento}")
    print("-" * 50)

print("\n=== Verificando Notas Fiscais com pedido ===\n")

nfs = NotaFiscalFutura.objects.exclude(fk_pedido__isnull=True)[:5]
for nf in nfs:
    print(f"NF: {nf.nro_nota}, Serie: {nf.serie}, FK_Pedido: {nf.fk_pedido}")

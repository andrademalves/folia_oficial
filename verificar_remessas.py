import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import RemessaCNAB

# Verificar remessas
remessas = RemessaCNAB.objects.all().order_by('-data_geracao')

print(f"\n=== REMESSAS CADASTRADAS ===")
print(f"Total: {remessas.count()}\n")

for r in remessas[:5]:
    print(f"ID: {r.id}")
    print(f"Nome Arquivo: {r.nome_arquivo}")
    print(f"Data Geração: {r.data_geracao}")
    print(f"Status: {r.status}")
    print(f"Quantidade Boletos: {r.boletos.count()}")
    print(f"Valor Total: R$ {r.valor_total:.2f}")
    print("-" * 50)

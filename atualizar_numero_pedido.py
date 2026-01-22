import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from contas_receber.models import NotaFiscal

print("🔄 Atualizando número de pedido das notas fiscais...\n")

# Atualizar notas de teste
notas = NotaFiscal.objects.filter(numero_pedido__isnull=True)

for nf in notas:
    # Gerar número de pedido baseado no número da nota
    # Simulando o padrão do Futura: 1398703, 1420003, etc.
    numero_base = int(nf.numero_nota) - 8000  # 8001 -> 1, 8002 -> 2, etc.
    nf.numero_pedido = f"{1398700 + numero_base}"
    nf.save()
    print(f"✅ NF {nf.numero_nota} -> numero_pedido: {nf.numero_pedido}")

print("\n✨ Números de pedido atualizados!")

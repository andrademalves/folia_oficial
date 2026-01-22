import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto, ConfiguracaoBancaria

# Verificar boletos disponíveis
boletos = Boleto.objects.filter(status='EMITIDO', enviado_banco=False)

print(f"\n=== BOLETOS DISPONÍVEIS PARA REMESSA ===")
print(f"Total: {boletos.count()}\n")

for b in boletos[:10]:
    print(f"ID: {b.id}")
    print(f"Cliente: {b.cliente.nome if b.cliente else 'N/A'}")
    print(f"Valor: R$ {b.valor_documento:.2f}")
    print(f"Vencimento: {b.data_vencimento}")
    print(f"Status: {b.status}")
    print(f"Configuração: {b.configuracao.id if b.configuracao else 'SEM CONFIGURAÇÃO!'}")
    print("-" * 50)

# Verificar configurações
configs = ConfiguracaoBancaria.objects.filter(ativo=True)
print(f"\n=== CONFIGURAÇÕES ATIVAS ===")
print(f"Total: {configs.count()}\n")

for c in configs:
    print(f"ID: {c.id}")
    print(f"Nome: {c.nome}")
    print(f"Código Banco: {c.codigo_banco}")
    print(f"Agência: {c.agencia} - Conta: {c.conta}")
    print(f"Código Beneficiário: {c.codigo_beneficiario}")
    print(f"Sequencial Arquivo: {c.sequencial_arquivo}")
    print("-" * 50)

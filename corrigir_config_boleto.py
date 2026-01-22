import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import ConfiguracaoBancaria

# Lista todas as configurações
configs = ConfiguracaoBancaria.objects.all()

print("=== Configurações Bancárias ===")
for config in configs:
    print(f"\nID: {config.id}")
    print(f"Nome: {config.nome}")
    print(f"Código Beneficiário: {config.codigo_beneficiario}")
    print(f"Agência: {config.agencia}")
    print(f"Conta: {config.conta}")
    print(f"Ativo: {config.ativo}")
    
    # Corrige se tiver "FACTORY"
    if config.codigo_beneficiario and 'FACTORY' in str(config.codigo_beneficiario).upper():
        print(">>> CORRIGINDO...")
        config.codigo_beneficiario = "123456"  # Valor exemplo
        config.agencia = config.agencia if config.agencia and str(config.agencia).isdigit() else "1234"
        config.conta = config.conta if config.conta and str(config.conta).isdigit() else "12345678"
        config.carteira = "1"
        config.modalidade = "14"
        config.save()
        print("✓ Configuração corrigida!")
        print(f"  Novo Código Beneficiário: {config.codigo_beneficiario}")
        print(f"  Nova Agência: {config.agencia}")
        print(f"  Nova Conta: {config.conta}")

print("\n=== Concluído ===")

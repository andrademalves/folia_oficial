"""
Teste da correção do campo livre do código de barras
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto, ConfiguracaoBancaria

# Buscar um boleto para teste
boleto = Boleto.objects.first()

if not boleto:
    print("❌ Nenhum boleto encontrado!")
    exit(1)

print("="*80)
print("TESTE DO CAMPO LIVRE - CÓDIGO DE BARRAS")
print("="*80)

config = boleto.configuracao
print(f"\n📋 Configuração:")
print(f"   Beneficiário: {config.codigo_beneficiario}")
print(f"   Carteira: {config.carteira}")
print(f"   Modalidade: {config.modalidade}")
print(f"   Nosso Número: {boleto.nosso_numero}")

# Testar geração do campo livre
beneficiario = str(config.codigo_beneficiario).zfill(6)
nosso_numero = str(boleto.nosso_numero).zfill(17)

print(f"\n🔢 Componentes:")
print(f"   Beneficiário (6): {beneficiario}")
print(f"   Nosso Número (17): {nosso_numero}")
print(f"   Carteira: {config.carteira}")
print(f"   Modalidade: {config.modalidade}")

# Simular construção do campo livre
from boletos.utils.codigo_barras import calcular_dv_nosso_numero_caixa

dv = calcular_dv_nosso_numero_caixa(nosso_numero, config.agencia, beneficiario)

campo_livre = beneficiario  # 6
campo_livre += dv  # 1 (total: 7)
campo_livre += nosso_numero[:3]  # 3 (total: 10)
campo_livre += str(config.carteira)[-1:]  # 1 (total: 11)
campo_livre += nosso_numero[3:15]  # 12 (total: 23)
campo_livre += str(config.modalidade).zfill(2)  # 2 (total: 25)

print(f"\n🏗️  Construção do Campo Livre:")
print(f"   Beneficiário (6): {beneficiario} ✓")
print(f"   DV (1): {dv} ✓")
print(f"   Primeiras 3 NN (3): {nosso_numero[:3]} ✓")
print(f"   Carteira (1): {str(config.carteira)[-1:]} ✓")
print(f"   Resto NN (12): {nosso_numero[3:15]} ✓")
print(f"   Modalidade (2): {str(config.modalidade).zfill(2)} ✓")

print(f"\n✅ Campo Livre: {campo_livre}")
print(f"   Tamanho: {len(campo_livre)} posições")

if len(campo_livre) == 25:
    print(f"\n✅ CORRETO! Campo livre tem exatamente 25 posições!")
else:
    print(f"\n❌ ERRO! Campo livre deveria ter 25 posições, mas tem {len(campo_livre)}!")

# Tentar gerar código de barras completo
print(f"\n🔨 Testando geração completa do código de barras...")
try:
    from boletos.utils.codigo_barras import gerar_codigo_barras
    codigo = gerar_codigo_barras(boleto)
    print(f"✅ Código de barras gerado com sucesso!")
    print(f"   Código: {codigo}")
    print(f"   Tamanho: {len(codigo)} posições (esperado: 44)")
    
    if len(codigo) == 44:
        print(f"\n✅ TUDO CERTO! Código de barras válido!")
    else:
        print(f"\n❌ ERRO! Código de barras deveria ter 44 posições!")
        
except Exception as e:
    print(f"❌ ERRO ao gerar código de barras:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

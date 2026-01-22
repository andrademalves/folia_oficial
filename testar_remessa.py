import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto, RemessaCNAB, ConfiguracaoBancaria
from boletos.utils.cnab240 import GeradorCNAB240
from django.utils import timezone

print("\n" + "="*80)
print("TESTE DE GERAÇÃO DE REMESSA CNAB 240")
print("="*80)

# Buscar boletos disponíveis
boletos_ids = list(Boleto.objects.filter(status='EMITIDO', enviado_banco=False).order_by('id').values_list('id', flat=True)[:3])
boletos = Boleto.objects.filter(id__in=boletos_ids)

print(f"\nBoletos selecionados: {boletos.count()}")
for b in boletos:
    print(f"  - Boleto {b.id}: {b.cliente.nome} - R$ {b.valor_documento:.2f}")

if not boletos.exists():
    print("\n❌ Nenhum boleto disponível!")
    exit()

try:
    # Busca configuração
    config = boletos.first().configuracao
    print(f"\nConfiguração: {config.nome}")
    print(f"Código Beneficiário: {config.codigo_beneficiario}")
    print(f"Sequencial Arquivo: {config.sequencial_arquivo}")
    
    # Gera o arquivo CNAB
    print("\nGerando arquivo CNAB 240...")
    gerador = GeradorCNAB240(config)
    conteudo_cnab = gerador.gerar_remessa(list(boletos))
    
    print(f"Arquivo gerado com {len(conteudo_cnab)} caracteres")
    print(f"Número de linhas: {len(conteudo_cnab.splitlines())}")
    
    # Valida o arquivo
    print("\nValidando arquivo...")
    valido, erros = gerador.validar_arquivo(conteudo_cnab)
    
    if not valido:
        print(f"❌ Arquivo CNAB inválido!")
        for erro in erros:
            print(f"  - {erro}")
        exit()
    
    print("✅ Arquivo válido!")
    
    # Cria o registro de remessa
    data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'CB{config.codigo_beneficiario.zfill(7)}_{data_hora}.REM'
    
    print(f"\nCriando registro de remessa: {nome_arquivo}")
    
    remessa = RemessaCNAB.objects.create(
        configuracao=config,
        numero_sequencial=config.sequencial_arquivo,
        tipo='CNAB240',
        nome_arquivo=nome_arquivo,
        conteudo=conteudo_cnab,
        quantidade_titulos=boletos.count(),
        valor_total=sum(b.valor_documento for b in boletos),
        status='GERADO'
    )
    
    print(f"✅ Remessa criada com ID: {remessa.id}")
    
    # Associa boletos à remessa
    remessa.boletos.set(boletos)
    print(f"✅ {boletos.count()} boletos associados")
    
    # Atualiza status dos boletos
    boletos.update(
        enviado_banco=True,
        data_envio_banco=timezone.now(),
        status='REGISTRADO'
    )
    print(f"✅ Status dos boletos atualizado para REGISTRADO")
    
    # Incrementa sequencial
    config.sequencial_arquivo += 1
    config.save(update_fields=['sequencial_arquivo'])
    print(f"✅ Sequencial incrementado para {config.sequencial_arquivo}")
    
    print("\n" + "="*80)
    print(f"✅ REMESSA GERADA COM SUCESSO!")
    print(f"ID da Remessa: {remessa.id}")
    print(f"Nome do Arquivo: {nome_arquivo}")
    print(f"Quantidade de Títulos: {remessa.quantidade_titulos}")
    print(f"Valor Total: R$ {remessa.valor_total:.2f}")
    print("="*80 + "\n")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERRO: {str(e)}")
    print("\nTraceback completo:")
    print(traceback.format_exc())

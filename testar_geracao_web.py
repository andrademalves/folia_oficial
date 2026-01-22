"""
Teste de geração de remessa CNAB através da interface web
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto, RemessaCNAB
from boletos.utils.cnab240_novo import GeradorCNAB240Caixa
from datetime import datetime

print("="*80)
print("TESTE DE GERAÇÃO DE REMESSA - NOVO GERADOR")
print("="*80)

# Buscar boletos disponíveis
boletos = Boleto.objects.filter(status='EMITIDO', enviado_banco=False)[:3]

if not boletos.exists():
    print("❌ Nenhum boleto disponível para teste!")
    exit(1)

print(f"\n✓ {boletos.count()} boletos selecionados:")
for b in boletos:
    print(f"  - Boleto #{b.id}: {b.cliente.nome if b.cliente else 'Sem cliente'} - R$ {b.valor_documento}")

# Pegar configuração
config = boletos.first().configuracao
print(f"\n✓ Configuração: {config.nome} - Banco {config.codigo_banco}")
print(f"  Ag {config.agencia}-{config.agencia_dv} / Conta {config.conta}-{config.conta_dv}")

# Gerar arquivo
print("\n⏳ Gerando arquivo CNAB 240...")
try:
    gerador = GeradorCNAB240Caixa(config)
    conteudo = gerador.gerar_remessa(list(boletos))
    
    # Verificar estrutura
    linhas = conteudo.strip().split('\r\n')
    print(f"\n✅ Arquivo gerado com sucesso!")
    print(f"   Total de linhas: {len(linhas)}")
    print(f"   Total de caracteres: {len(conteudo)}")
    
    # Validar tamanho das linhas
    todos_240 = all(len(linha) == 240 for linha in linhas if linha)
    if todos_240:
        print(f"   ✅ Todas as linhas têm 240 caracteres")
    else:
        print(f"   ❌ ERRO: Linhas com tamanho incorreto!")
        for i, linha in enumerate(linhas, 1):
            if linha and len(linha) != 240:
                print(f"      Linha {i}: {len(linha)} caracteres")
    
    # Salvar arquivo (usar newline='' para não converter \r\n)
    nome_arquivo = f'TESTE_WEB_{datetime.now().strftime("%Y%m%d_%H%M%S")}.REM'
    with open(nome_arquivo, 'w', encoding='ascii', newline='') as f:
        f.write(conteudo)
    
    print(f"\n✅ Arquivo salvo: {nome_arquivo}")
    
    # Mostrar preview
    print("\n" + "="*80)
    print("PREVIEW DO ARQUIVO (primeiras 5 linhas):")
    print("="*80)
    for i, linha in enumerate(linhas[:5], 1):
        tipo = linha[7:8] if len(linha) > 7 else '?'
        tipo_nome = {
            '0': 'HEADER ARQUIVO',
            '1': 'HEADER LOTE',
            '3': 'DETALHE',
            '5': 'TRAILER LOTE',
            '9': 'TRAILER ARQUIVO'
        }.get(tipo, 'DESCONHECIDO')
        print(f"\nLinha {i} ({tipo_nome}):")
        print(f"  Pos 001-003 (Banco): {linha[0:3]}")
        print(f"  Pos 008-008 (Tipo): {linha[7:8]}")
        if tipo == '3':
            seg = linha[13:14] if len(linha) > 13 else '?'
            print(f"  Pos 014-014 (Segmento): {seg}")
        print(f"  Tamanho: {len(linha)} caracteres")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print(f"\n📄 Arquivo: {nome_arquivo}")
    print(f"📊 {boletos.count()} título(s) incluído(s)")
    print(f"💰 Valor total: R$ {sum(b.valor_documento for b in boletos):.2f}")
    print("\n⚠️  IMPORTANTE: Este é um teste local. Use a interface web para geração oficial:")
    print("   http://127.0.0.1:8000/boletos/remessas/gerar/")
    
except Exception as e:
    import traceback
    print(f"\n❌ ERRO ao gerar arquivo:")
    print(traceback.format_exc())
    exit(1)

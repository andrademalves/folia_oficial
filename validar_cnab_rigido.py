import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto
from boletos.utils.cnab240 import GeradorCNAB240

# Resetar boletos para teste
Boleto.objects.filter(status='REGISTRADO').update(status='EMITIDO', enviado_banco=False, data_envio_banco=None)

print("\n" + "="*100)
print("VALIDAÇÃO RIGOROSA DO ARQUIVO CNAB 240 - PADRÃO CAIXA")
print("="*100)

# Buscar boletos
boletos_ids = list(Boleto.objects.filter(status='EMITIDO', enviado_banco=False).order_by('id').values_list('id', flat=True)[:3])
boletos = list(Boleto.objects.filter(id__in=boletos_ids))

if not boletos:
    print("\n❌ Nenhum boleto disponível para teste!")
    exit()

print(f"\n✓ {len(boletos)} boletos selecionados para teste")

# Gerar arquivo
config = boletos[0].configuracao
gerador = GeradorCNAB240(config)
conteudo = gerador.gerar_remessa(boletos)

# Análise rigorosa
print("\n" + "-"*100)
print("ANÁLISE DE FORMATO")
print("-"*100)

linhas = conteudo.split('\r\n')
erros_criticos = []
warnings = []

print(f"\n📊 Total de linhas: {len(linhas)}")
print(f"📊 Total de caracteres: {len(conteudo)}")
print(f"📊 Separador de linha: \\r\\n (CRLF - padrão Windows/bancário)")

# Verificação linha por linha
print("\n" + "-"*100)
print("VERIFICAÇÃO LINHA POR LINHA")
print("-"*100)

for i, linha in enumerate(linhas, 1):
    # Ignorar linhas vazias no final
    if not linha:
        if i == len(linhas):
            warnings.append(f"Linha {i}: Linha vazia no final do arquivo (pode ser ignorada)")
        else:
            erros_criticos.append(f"Linha {i}: Linha vazia no meio do arquivo")
        continue
    
    tamanho = len(linha)
    
    # Verificar tamanho exato
    if tamanho != 240:
        erros_criticos.append(f"Linha {i}: Tamanho INCORRETO! {tamanho} posições (esperado: 240)")
        print(f"❌ Linha {i:2d}: {tamanho:3d} posições - ERRO CRÍTICO!")
        print(f"   Conteúdo: '{linha[:60]}...'")
        continue
    
    # Verificar caracteres inválidos
    tem_tab = '\t' in linha
    tem_quebra = '\n' in linha or '\r' in linha
    
    if tem_tab:
        erros_criticos.append(f"Linha {i}: Contém TAB (\\t) - PROIBIDO!")
    
    if tem_quebra:
        erros_criticos.append(f"Linha {i}: Contém quebra de linha (\\n ou \\r) - PROIBIDO!")
    
    # Identificar tipo de registro
    codigo_banco = linha[0:3]
    tipo_reg = linha[7:8]
    
    tipo_desc = {
        '0': 'HEADER ARQUIVO',
        '1': 'HEADER LOTE',
        '3': f'DETALHE - Seg {linha[13:14] if len(linha) > 13 else "?"}',
        '5': 'TRAILER LOTE',
        '9': 'TRAILER ARQUIVO'
    }.get(tipo_reg, f'DESCONHECIDO ({tipo_reg})')
    
    print(f"✓ Linha {i:2d}: 240 posições - {tipo_desc} - Banco: {codigo_banco}")

# Verificações adicionais
print("\n" + "-"*100)
print("VERIFICAÇÕES ESTRUTURAIS")
print("-"*100)

# Header arquivo
if linhas[0][7:8] != '0':
    erros_criticos.append("Header do arquivo: Tipo de registro inválido (pos 8 deve ser '0')")
else:
    print("✓ Header do arquivo: OK (tipo registro = '0')")

# Trailer arquivo
ultima_linha_valida = [l for l in linhas if l][-1]
if ultima_linha_valida[7:8] != '9':
    erros_criticos.append("Trailer do arquivo: Tipo de registro inválido (pos 8 deve ser '9')")
else:
    print("✓ Trailer do arquivo: OK (tipo registro = '9')")

# Código do banco
codigo_banco_header = linhas[0][0:3]
if codigo_banco_header != '104':
    erros_criticos.append(f"Código do banco incorreto: '{codigo_banco_header}' (esperado: '104' - CAIXA)")
else:
    print("✓ Código do banco: 104 (CAIXA ECONÔMICA FEDERAL)")

# Código CNAB
cnab = linhas[0][140:142]
if cnab != '05':
    erros_criticos.append(f"Código CNAB incorreto: '{cnab}' (esperado: '05' para CNAB 240)")
    print(f"❌ Código CNAB (pos 141-142): '{cnab}' - DEVE SER '05'")
    print(f"   Header completo pos 130-150: '{linhas[0][129:149]}'")
else:
    print("✓ Código CNAB: 05 (CNAB 240)")

# Verificar encoding
print("\n" + "-"*100)
print("VERIFICAÇÃO DE ENCODING")
print("-"*100)

try:
    # Tentar codificar em ASCII (padrão bancário)
    conteudo_ascii = conteudo.encode('ascii')
    print("✓ Encoding: ASCII puro (compatível)")
except UnicodeEncodeError as e:
    erros_criticos.append(f"Encoding: Contém caracteres não-ASCII! {e}")
    print(f"❌ Encoding: ERRO - Contém caracteres especiais não permitidos")

# Verificar se termina corretamente
if conteudo.endswith('\r\n\r\n'):
    warnings.append("Arquivo termina com dupla quebra de linha (pode causar problemas)")
    print("⚠ Terminação: Dupla quebra de linha detectada")
elif conteudo.endswith('\r\n'):
    warnings.append("Arquivo termina com quebra de linha (alguns bancos rejeitam isso)")
    print("⚠ Terminação: Arquivo termina com \\r\\n (verificar se banco aceita)")
else:
    print("✓ Terminação: Sem quebra de linha extra no final")

# RESULTADO FINAL
print("\n" + "="*100)
print("RESULTADO DA VALIDAÇÃO")
print("="*100)

if erros_criticos:
    print(f"\n❌ ARQUIVO INVÁLIDO! {len(erros_criticos)} erro(s) crítico(s) encontrado(s):")
    for erro in erros_criticos:
        print(f"   • {erro}")
else:
    print("\n✅ ARQUIVO VÁLIDO! Todas as verificações críticas passaram.")

if warnings:
    print(f"\n⚠ {len(warnings)} aviso(s):")
    for warning in warnings:
        print(f"   • {warning}")

# Mostrar preview de algumas linhas
print("\n" + "="*100)
print("PREVIEW DO ARQUIVO (primeiras 3 linhas)")
print("="*100)

for i, linha in enumerate(linhas[:3], 1):
    if linha:
        print(f"\nLinha {i} ({len(linha)} posições):")
        print(f"Pos 001-020: '{linha[0:20]}'")
        print(f"Pos 021-040: '{linha[20:40]}'")
        print(f"Pos 041-060: '{linha[40:60]}'")
        print(f"Pos 061-080: '{linha[60:80]}'")
        print(f"...")
        print(f"Pos 221-240: '{linha[220:240]}'")

print("\n" + "="*100)

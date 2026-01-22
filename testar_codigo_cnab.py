import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto
from boletos.utils.cnab240 import GeradorCNAB240

# Resetar boletos para teste
Boleto.objects.filter(status='REGISTRADO').update(status='EMITIDO', enviado_banco=False, data_envio_banco=None)

print("\n✓ Boletos resetados")

# Buscar boletos
boletos = list(Boleto.objects.filter(status='EMITIDO', enviado_banco=False).order_by('id')[:3])

if not boletos:
    print("\n❌ Nenhum boleto disponível!")
    exit()

# Gerar arquivo
config = boletos[0].configuracao
gerador = GeradorCNAB240(config)
conteudo = gerador.gerar_remessa(boletos)

linhas = conteudo.split('\r\n')
header = linhas[0]

print("\n" + "="*100)
print("ANÁLISE DETALHADA DO HEADER DO ARQUIVO (Linha 1)")
print("="*100)

print(f"\nTamanho total: {len(header)} posições")
print(f"\nPosição 001-003 (Código Banco): '{header[0:3]}'")
print(f"Posição 004-007 (Lote): '{header[3:7]}'")
print(f"Posição 008 (Tipo Registro): '{header[7:8]}'")
print(f"Posição 009-017 (Brancos): '{header[8:17]}'")
print(f"Posição 018 (Tipo Inscrição): '{header[17:18]}'")
print(f"Posição 019-032 (CNPJ): '{header[18:32]}'")
print(f"Posição 033-052 (Convênio): '{header[32:52]}'")
print(f"Posição 053-057 (Agência): '{header[52:57]}'")
print(f"Posição 058 (DV Agência): '{header[57:58]}'")
print(f"Posição 059-070 (Conta): '{header[58:70]}'")
print(f"Posição 071 (DV Conta): '{header[70:71]}'")
print(f"Posição 072 (DV Ag/Conta): '{header[71:72]}'")
print(f"Posição 073-102 (Nome Empresa): '{header[72:102]}'")
print(f"Posição 103-132 (Nome Banco): '{header[102:132]}'")
print(f"Posição 133-140 (Brancos): '{header[132:140]}'")
print(f"Posição 141-142 (Código CNAB): '{header[140:142]}' ← DEVE SER '05'")
print(f"Posição 143 (Código Remessa): '{header[142:143]}'")
print(f"Posição 144-151 (Data Geração): '{header[143:151]}'")
print(f"Posição 152-157 (Hora Geração): '{header[151:157]}'")
print(f"Posição 158-163 (Sequencial): '{header[157:163]}'")
print(f"Posição 164-166 (Versão Layout): '{header[163:166]}'")
print(f"Posição 167-171 (Densidade): '{header[166:171]}'")
print(f"Posição 172-240 (Brancos): '{header[171:240]}'")

codigo_cnab = header[140:142]

print("\n" + "="*100)
if codigo_cnab == '05':
    print("✅ CÓDIGO CNAB CORRETO: '05'")
else:
    print(f"❌ CÓDIGO CNAB INCORRETO: '{codigo_cnab}' (esperado '05')")
print("="*100)

# Salvar arquivo para inspeção
with open('arquivo_cnab_teste.rem', 'w') as f:
    f.write(conteudo)

print("\n✓ Arquivo salvo em: arquivo_cnab_teste.rem")
print(f"✓ {len(linhas)} linhas")
print(f"✓ {len(conteudo)} caracteres totais")

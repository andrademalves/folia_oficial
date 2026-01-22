import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto
from datetime import date

b = Boleto.objects.first()
base = date(1997, 10, 7)
venc = b.data_vencimento if isinstance(b.data_vencimento, date) else b.data_vencimento.date()
delta = (venc - base).days

print(f'Data vencimento: {venc}')
print(f'Data base: {base}')
print(f'Delta (dias): {delta}')
print(f'Delta str: "{str(delta)}"')
print(f'Delta zfill(4): "{str(delta).zfill(4)}"')
print(f'Tamanho: {len(str(delta).zfill(4))}')

# O problema é que zfill não LIMITA, apenas PREENCHE!
# Se o número já tem mais de 4 dígitos, ele mantém todos
print(f'\n⚠️  PROBLEMA: zfill(4) não limita o tamanho!')
print(f'   Se delta > 9999, o resultado terá mais de 4 dígitos')

# Solução: pegar apenas os últimos 4 dígitos ou validar
print(f'\nSolução 1 (últimos 4): "{str(delta)[-4:].zfill(4)}"')
print(f'Solução 2 (módulo 10000): "{str(delta % 10000).zfill(4)}"')

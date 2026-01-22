import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from importacoes.models import ContaParcelaFutura, NotaFiscalFutura

# Verificar nota
nf = NotaFiscalFutura.objects.filter(nro_nota=3864).first()
print(f"Nota encontrada: {nf}")
if nf:
    print(f"  ID: {nf.id}")
    print(f"  Nro Nota: {nf.nro_nota}")
    print(f"  Total Nota: {nf.total_nota}")
    print(f"  Parcelas Lancadas: {nf.parcelas_lancadas}")
    
    # Buscar parcelas
    parcelas = ContaParcelaFutura.objects.filter(documento__startswith=f'NT:{nf.nro_nota} ')
    print(f"\nParcelas encontradas com 'NT:{nf.nro_nota} ': {parcelas.count()}")
    
    # Mostrar algumas parcelas
    for p in parcelas[:5]:
        print(f"  - ID: {p.id}, Doc: {p.documento}, Valor: {p.valor_parcela}, Venc: {p.data_vencimento}")
    
    # Tentar buscar de outras formas
    parcelas2 = ContaParcelaFutura.objects.filter(documento__contains=str(nf.nro_nota))
    print(f"\nParcelas com documento contendo '{nf.nro_nota}': {parcelas2.count()}")
    for p in parcelas2[:5]:
        print(f"  - ID: {p.id}, Doc: {p.documento}, Valor: {p.valor_parcela}")
else:
    print("Nota 3864 não encontrada!")

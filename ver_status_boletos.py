import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto

boletos = Boleto.objects.all()
print(f"\nTotal de boletos: {boletos.count()}\n")

for b in boletos:
    print(f"Boleto {b.id}: Status={b.status}, Enviado={b.enviado_banco}")

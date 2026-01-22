import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from boletos.models import Boleto, RemessaCNAB

# Deletar remessa de teste
remessas = RemessaCNAB.objects.all()
print(f"\n✅ Deletando {remessas.count()} remessa(s)...")
remessas.delete()

# Resetar boletos para EMITIDO
boletos = Boleto.objects.filter(status='REGISTRADO')
print(f"✅ Resetando {boletos.count()} boleto(s) para EMITIDO...")
boletos.update(status='EMITIDO', enviado_banco=False, data_envio_banco=None)

print("\n✅ Pronto! Agora você pode testar a geração de remessa pela interface.\n")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from django.core.cache import cache
from django.contrib.sessions.models import Session

print("="*80)
print("LIMPANDO CACHE E SESSÕES")
print("="*80)

# Limpar cache
try:
    cache.clear()
    print("\n✓ Cache limpo com sucesso")
except Exception as e:
    print(f"\n✗ Erro ao limpar cache: {e}")

# Limpar todas as sessões
try:
    count = Session.objects.all().delete()[0]
    print(f"✓ {count} sessões removidas com sucesso")
    print("\n  IMPORTANTE: Todos os usuários precisarão fazer login novamente!")
except Exception as e:
    print(f"\n✗ Erro ao limpar sessões: {e}")

print("\n" + "="*80)
print("Reinicie o servidor e faça login novamente")
print("="*80)

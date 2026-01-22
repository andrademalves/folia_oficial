import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Menu

print("="*80)
print("VERIFICANDO URLS USADAS EM DECORATORS MAS NÃO EXISTENTES NO BANCO")
print("="*80)

# URLs usadas em decorators
urls_decorators = [
    '/boletos/remessas/gerar/',
]

print("\nVerificando URLs:\n")

for url in urls_decorators:
    try:
        menu = Menu.objects.get(url=url, ativo=True)
        print(f"✓ {url:40} - Existe (ID: {menu.id}, Menu: {menu.nome})")
    except Menu.DoesNotExist:
        print(f"✗ {url:40} - NÃO EXISTE")
        # Tentar encontrar similar
        similar = Menu.objects.filter(url__contains=url.split('/')[1], ativo=True)
        if similar.exists():
            print(f"  Menus similares encontrados:")
            for m in similar[:3]:
                print(f"    - {m.url} ({m.nome})")

print("\n" + "="*80)

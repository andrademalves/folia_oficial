import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu

print("🚀 Criando módulo Contas a Receber...")

# Criar ou atualizar módulo
modulo, created = Modulo.objects.get_or_create(
    nome='Contas a Receber',
    defaults={
        'descricao': 'Gestão de contas a receber, notas fiscais, parcelas e créditos',
        'icone': 'fas fa-receipt',
        'ordem': 4,
        'ativo': True
    }
)

if created:
    print(f"✅ Módulo criado: {modulo.nome}")
else:
    print(f"ℹ️  Módulo já existe: {modulo.nome}")

# Criar menus
menus_data = [
    {'nome': 'Dashboard', 'url': '/contas-receber/', 'icone': 'fas fa-home', 'ordem': 1},
    {'nome': 'Notas Fiscais', 'url': '/contas-receber/notas-fiscais/', 'icone': 'fas fa-file-invoice', 'ordem': 2},
    {'nome': 'Parcelas', 'url': '/contas-receber/parcelas/', 'icone': 'fas fa-calendar-alt', 'ordem': 3},
    {'nome': 'Por Vencimento', 'url': '/contas-receber/parcelas/vencimento/', 'icone': 'fas fa-clock', 'ordem': 4},
    {'nome': 'Dar Baixa', 'url': '/contas-receber/parcelas/baixa/', 'icone': 'fas fa-check-circle', 'ordem': 5},
    {'nome': 'Créditos', 'url': '/contas-receber/creditos/', 'icone': 'fas fa-credit-card', 'ordem': 6},
    {'nome': 'Origens', 'url': '/contas-receber/origens/', 'icone': 'fas fa-tags', 'ordem': 7},
]

for menu_data in menus_data:
    menu, created = Menu.objects.get_or_create(
        modulo=modulo,
        nome=menu_data['nome'],
        defaults={
            'url': menu_data['url'],
            'icone': menu_data['icone'],
            'ordem': menu_data['ordem'],
            'ativo': True
        }
    )
    if created:
        print(f"✅ Menu criado: {menu.nome}")
    else:
        print(f"ℹ️  Menu já existe: {menu.nome}")

print("\n✨ Módulo Contas a Receber configurado com sucesso!")
print(f"📊 Total de menus: {Menu.objects.filter(modulo=modulo).count()}")

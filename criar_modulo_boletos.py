"""
Script para criar módulo e menus de Boletos no sistema
Execute: python criar_modulo_boletos.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestaoTi.settings')
django.setup()

from usuarios.models import Modulo, Menu, PermissaoMenu
from django.contrib.auth.models import User

def criar_modulo_boletos():
    print("=" * 80)
    print("CRIANDO MÓDULO DE BOLETOS BANCÁRIOS")
    print("=" * 80)
    
    # Cria ou atualiza módulo
    modulo, criado = Modulo.objects.get_or_create(
        nome='Boletos',
        defaults={
            'icone': 'fas fa-barcode',
            'ordem': 6
        }
    )
    
    if criado:
        print(f"✅ Módulo '{modulo.nome}' criado com sucesso!")
    else:
        print(f"ℹ️  Módulo '{modulo.nome}' já existe. Atualizando...")
        modulo.icone = 'fas fa-barcode'
        modulo.ordem = 6
        modulo.save()
        print(f"✅ Módulo '{modulo.nome}' atualizado!")
    
    # Define menus
    menus_data = [
        {
            'nome': 'Dashboard',
            'icone': 'fas fa-home',
            'url': '/boletos/',
            'ordem': 1
        },
        {
            'nome': 'Listar Boletos',
            'icone': 'fas fa-list',
            'url': '/boletos/boletos/',
            'ordem': 2
        },
        {
            'nome': 'Gerar Remessa',
            'icone': 'fas fa-file-export',
            'url': '/boletos/remessas/gerar/',
            'ordem': 3
        },
        {
            'nome': 'Remessas CNAB',
            'icone': 'fas fa-folder-open',
            'url': '/boletos/remessas/',
            'ordem': 4
        },
    ]
    
    print("\nCriando menus...")
    for menu_data in menus_data:
        menu, criado = Menu.objects.get_or_create(
            modulo=modulo,
            nome=menu_data['nome'],
            defaults=menu_data
        )
        
        if criado:
            print(f"  ✅ Menu '{menu.nome}' criado")
        else:
            print(f"  ℹ️  Menu '{menu.nome}' já existe")
            # Atualiza dados
            for key, value in menu_data.items():
                setattr(menu, key, value)
            menu.save()
    
    # Conta menus criados
    total_menus = Menu.objects.filter(modulo=modulo).count()
    print(f"\n✅ Total de {total_menus} menus no módulo Boletos")
    
    # Pergunta se quer dar permissões ao usuário atual
    print("\n" + "=" * 80)
    print("PERMISSÕES")
    print("=" * 80)
    
    usuarios = User.objects.all()
    print(f"\nUsuários cadastrados: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"\n  - {usuario.username}")
    
    username = input("\nDigite o username do usuário para dar permissões (ou Enter para pular): ").strip()
    
    if username:
        try:
            usuario = User.objects.get(username=username)
            menus = Menu.objects.filter(modulo=modulo)
            
            print(f"\nCriando permissões para {usuario.username}...")
            
            for menu in menus:
                # Cria permissão com CRUD completo
                permissao, criado = PermissaoMenu.objects.get_or_create(
                    usuario=usuario,
                    menu=menu,
                    tipo='usuario',
                    defaults={
                        'pode_visualizar': True,
                        'pode_criar': True,
                        'pode_editar': True,
                        'pode_excluir': True
                    }
                )
                
                if criado:
                    print(f"  ✅ Permissão criada para menu '{menu.nome}'")
                else:
                    # Atualiza permissões
                    permissao.pode_visualizar = True
                    permissao.pode_criar = True
                    permissao.pode_editar = True
                    permissao.pode_deletar = True
                    permissao.save()
                    print(f"  ℹ️  Permissão atualizada para menu '{menu.nome}'")
            
            print(f"\n✅ Permissões configuradas para {usuario.username}")
            
        except User.DoesNotExist:
            print(f"❌ Usuário '{email}' não encontrado")
    
    print("\n" + "=" * 80)
    print("INSTALAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print("\nPróximos passos:")
    print("1. Executar migrations: python manage.py makemigrations boletos")
    print("2. Aplicar migrations: python manage.py migrate boletos")
    print("3. Instalar dependências: pip install reportlab python-barcode pillow")
    print("4. Configurar dados bancários no Admin Django")
    print("5. Acessar /boletos/ para começar a usar")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    criar_modulo_boletos()

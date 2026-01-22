from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import Menu, PermissaoMenu


class Command(BaseCommand):
    help = 'Atribui todas as permissões dos menus ao superusuário'

    def handle(self, *args, **kwargs):
        # Busca o primeiro superusuário
        try:
            superusuario = User.objects.filter(is_superuser=True).first()
            if not superusuario:
                self.stdout.write(self.style.ERROR('❌ Nenhum superusuário encontrado!'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao buscar superusuário: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Atribuindo permissões ao usuário: {superusuario.username}'))

        # Remove permissões antigas do usuário
        PermissaoMenu.objects.filter(usuario=superusuario).delete()

        # Busca todos os menus ativos
        menus = Menu.objects.filter(ativo=True)
        
        if not menus.exists():
            self.stdout.write(self.style.WARNING('⚠ Nenhum menu encontrado!'))
            self.stdout.write(self.style.WARNING('Execute: python manage.py popular_dados'))
            return

        # Cria permissões para todos os menus
        count = 0
        for menu in menus:
            PermissaoMenu.objects.create(
                tipo='usuario',
                usuario=superusuario,
                menu=menu,
                pode_visualizar=True,
                pode_criar=True,
                pode_editar=True,
                pode_excluir=True
            )
            count += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ Permissão criada para: {menu.nome}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {count} permissões atribuídas com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'✅ O usuário {superusuario.username} agora tem acesso total ao sistema!'))

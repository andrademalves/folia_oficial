from django.core.management.base import BaseCommand
from usuarios.models import Modulo, Menu

class Command(BaseCommand):
    help = 'Popula o módulo de importações e seus menus'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população do módulo de importações...'))

        # Criar módulo Importações
        modulo_importacoes, created = Modulo.objects.get_or_create(
            nome='Importações',
            defaults={
                'descricao': 'Importação de dados do sistema Futura',
                'icone': 'fas fa-download',
                'ordem': 3,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Módulo "{modulo_importacoes.nome}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Módulo "{modulo_importacoes.nome}" já existe.'))

        # Criar menus do módulo Importações
        menus = [
            {
                'nome': 'Dashboard',
                'descricao': 'Visão geral das importações',
                'url': '/importacoes/',
                'icone': 'fas fa-tachometer-alt',
                'ordem': 1
            },
            {
                'nome': 'Cadastro Geral',
                'descricao': 'Importar cadastro geral do Futura',
                'url': '/importacoes/cadastro-geral/',
                'icone': 'fas fa-address-book',
                'ordem': 2
            },
            {
                'nome': 'Notas Fiscais',
                'descricao': 'Importar notas fiscais do Futura',
                'url': '/importacoes/notas-fiscais/',
                'icone': 'fas fa-file-invoice',
                'ordem': 3
            }
        ]

        for menu_data in menus:
            menu, created = Menu.objects.get_or_create(
                modulo=modulo_importacoes,
                url=menu_data['url'],
                defaults={
                    'nome': menu_data['nome'],
                    'descricao': menu_data['descricao'],
                    'icone': menu_data['icone'],
                    'ordem': menu_data['ordem'],
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Menu "{menu.nome}" criado!'))
            else:
                self.stdout.write(self.style.WARNING(f'  Menu "{menu.nome}" já existe.'))

        self.stdout.write(self.style.SUCCESS('\nPopulação do módulo de importações concluída!'))

from django.core.management.base import BaseCommand
from usuarios.models import Modulo, Menu

class Command(BaseCommand):
    help = 'Popula o módulo de cadastros e seus menus'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população do módulo de cadastros...'))

        modulo, created = Modulo.objects.get_or_create(
            nome='Cadastros',
            defaults={
                'descricao': 'Cadastros mestres do sistema',
                'icone': 'fas fa-list',
                'ordem': 4,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Módulo "{modulo.nome}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Módulo "{modulo.nome}" já existe.'))

        menus = [
            {
                'nome': 'Dashboard',
                'descricao': 'Visão geral dos cadastros',
                'url': '/cadastros/',
                'icone': 'fas fa-home',
                'ordem': 1
            },
            {
                'nome': 'Plano de Contas',
                'descricao': 'Estrutura compatível com Futura',
                'url': '/cadastros/plano-contas/',
                'icone': 'fas fa-sitemap',
                'ordem': 2
            },
            {
                'nome': 'Contas Financeiras',
                'descricao': 'Bancos e Factory',
                'url': '/cadastros/contas-financeiras/',
                'icone': 'fas fa-university',
                'ordem': 3
            },
        ]

        for m in menus:
            obj, created = Menu.objects.get_or_create(
                modulo=modulo,
                url=m['url'],
                defaults={
                    'nome': m['nome'],
                    'descricao': m['descricao'],
                    'icone': m['icone'],
                    'ordem': m['ordem'],
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Menu "{obj.nome}" criado!'))
            else:
                self.stdout.write(self.style.WARNING(f'  Menu "{obj.nome}" já existe.'))

        self.stdout.write(self.style.SUCCESS('\nPopulação do módulo de cadastros concluída!'))

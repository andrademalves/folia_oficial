from django.core.management.base import BaseCommand
from usuarios.models import Modulo, Menu

class Command(BaseCommand):
    help = 'Popula o módulo financeiro e seus menus'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população do módulo financeiro...'))

        # Criar módulo Financeiro
        modulo_financeiro, created = Modulo.objects.get_or_create(
            nome='Financeiro',
            defaults={
                'descricao': 'Gestão financeira completa',
                'icone': 'fas fa-wallet',
                'ordem': 2,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Módulo "{modulo_financeiro.nome}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Módulo "{modulo_financeiro.nome}" já existe.'))

        # Criar menus do módulo Financeiro
        menus = [
            {
                'nome': 'Dashboard Financeiro',
                'descricao': 'Visão geral das finanças',
                'url': '/financeiro/',
                'icone': 'fas fa-chart-line',
                'ordem': 1
            },
            {
                'nome': 'Contas a Pagar',
                'descricao': 'Gestão de contas a pagar',
                'url': '/financeiro/contas-pagar/',
                'icone': 'fas fa-file-invoice-dollar',
                'ordem': 2
            },
            {
                'nome': 'Relatórios',
                'descricao': 'Relatórios financeiros',
                'url': '/financeiro/relatorios/',
                'icone': 'fas fa-chart-bar',
                'ordem': 3
            }
        ]

        for menu_data in menus:
            menu, created = Menu.objects.get_or_create(
                modulo=modulo_financeiro,
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

        self.stdout.write(self.style.SUCCESS('\nPopulação do módulo financeiro concluída!'))

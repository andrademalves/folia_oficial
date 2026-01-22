from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from usuarios.models import Modulo, Menu, PermissaoMenu


class Command(BaseCommand):
    help = 'Cria o módulo de Aprovações no sistema'

    def handle(self, *args, **kwargs):
        # Criar ou obter o módulo
        modulo, created = Modulo.objects.get_or_create(
            nome='Aprovações',
            defaults={
                'descricao': 'Módulo para aprovar solicitações de créditos e outras aprovações',
                'icone': 'fas fa-check-circle',
                'ordem': 5,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Módulo "{modulo.nome}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Módulo "{modulo.nome}" já existe.'))
        
        # Criar menu de aprovações de créditos
        menu, created = Menu.objects.get_or_create(
            modulo=modulo,
            url='/contas-receber/aprovacoes/',
            defaults={
                'nome': 'Créditos Pendentes',
                'descricao': 'Aprovar ou rejeitar solicitações de crédito',
                'icone': 'fas fa-credit-card',
                'ordem': 1,
                'ativo': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Menu "{menu.nome}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Menu "{menu.nome}" já existe.'))
        
        # Dar permissões aos grupos Diretoria e Administrativo
        grupos = ['Diretoria', 'Administrativo']
        for grupo_nome in grupos:
            try:
                grupo = Group.objects.get(name=grupo_nome)
                permissao, created = PermissaoMenu.objects.get_or_create(
                    tipo='grupo',
                    grupo=grupo,
                    menu=menu,
                    defaults={
                        'pode_visualizar': True,
                        'pode_criar': False,
                        'pode_editar': True,  # Aprovar/Rejeitar
                        'pode_excluir': False
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Permissão concedida ao grupo "{grupo_nome}"'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ Grupo "{grupo_nome}" já tem permissão'))
                    
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Grupo "{grupo_nome}" não encontrado'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Módulo de Aprovações configurado com sucesso!'))
        self.stdout.write(self.style.SUCCESS('Acesse http://127.0.0.1:8000/ para ver o novo módulo'))

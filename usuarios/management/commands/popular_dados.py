from django.core.management.base import BaseCommand
from usuarios.models import Modulo, Menu


class Command(BaseCommand):
    help = 'Popula o banco de dados com módulos e menus iniciais'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Criando módulos e menus iniciais...'))

        # Limpa dados existentes (opcional)
        Menu.objects.all().delete()
        Modulo.objects.all().delete()

        # ===========================================
        # MÓDULO USUÁRIOS
        # ===========================================
        modulo_usuarios = Modulo.objects.create(
            nome='Usuários',
            descricao='Módulo de gestão de usuários e permissões',
            icone='fas fa-users-cog',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Módulo criado: {modulo_usuarios.nome}'))

        Menu.objects.create(
            modulo=modulo_usuarios,
            nome='Dashboard',
            descricao='Dashboard de usuários',
            url='/dashboard/',
            icone='fas fa-tachometer-alt',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Dashboard'))

        Menu.objects.create(
            modulo=modulo_usuarios,
            nome='Gerenciar Usuários',
            descricao='Gestão de usuários do sistema',
            url='/usuarios/',
            icone='fas fa-users',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Gerenciar Usuários'))

        # ===========================================
        # MÓDULO CADASTROS
        # ===========================================
        modulo_cadastros = Modulo.objects.create(
            nome='Cadastros',
            descricao='Módulo de cadastros básicos',
            icone='fas fa-database',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Módulo criado: {modulo_cadastros.nome}'))

        Menu.objects.create(
            modulo=modulo_cadastros,
            nome='Dashboard',
            descricao='Dashboard de cadastros',
            url='/cadastros/dashboard/',
            icone='fas fa-tachometer-alt',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Dashboard'))

        Menu.objects.create(
            modulo=modulo_cadastros,
            nome='Plano de Contas',
            descricao='Gestão do plano de contas',
            url='/cadastros/plano-contas/',
            icone='fas fa-sitemap',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Plano de Contas'))

        Menu.objects.create(
            modulo=modulo_cadastros,
            nome='Contas Financeiras',
            descricao='Gestão de contas financeiras',
            url='/cadastros/contas-financeiras/',
            icone='fas fa-university',
            ordem=3,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Contas Financeiras'))

        Menu.objects.create(
            modulo=modulo_cadastros,
            nome='Métodos de Pagamento',
            descricao='Gestão de métodos de pagamento',
            url='/cadastros/metodos-pagamento/',
            icone='fas fa-credit-card',
            ordem=4,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Métodos de Pagamento'))

        Menu.objects.create(
            modulo=modulo_cadastros,
            nome='Relatórios',
            descricao='Relatórios de cadastros',
            url='/cadastros/relatorios/',
            icone='fas fa-chart-bar',
            ordem=5,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Relatórios'))

        # ===========================================
        # MÓDULO FINANCEIRO
        # ===========================================
        modulo_financeiro = Modulo.objects.create(
            nome='Financeiro',
            descricao='Módulo de gestão financeira',
            icone='fas fa-dollar-sign',
            ordem=3,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Módulo criado: {modulo_financeiro.nome}'))

        Menu.objects.create(
            modulo=modulo_financeiro,
            nome='Dashboard',
            descricao='Dashboard financeiro',
            url='/financeiro/dashboard/',
            icone='fas fa-tachometer-alt',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Dashboard'))

        Menu.objects.create(
            modulo=modulo_financeiro,
            nome='Contas a Pagar',
            descricao='Gestão de contas a pagar',
            url='/financeiro/contas-pagar/',
            icone='fas fa-file-invoice-dollar',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Contas a Pagar'))

        Menu.objects.create(
            modulo=modulo_financeiro,
            nome='Conta Corrente',
            descricao='Gestão de conta corrente',
            url='/financeiro/conta-corrente/',
            icone='fas fa-university',
            ordem=3,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Conta Corrente'))

        Menu.objects.create(
            modulo=modulo_financeiro,
            nome='Relatórios',
            descricao='Relatórios financeiros',
            url='/financeiro/relatorios/',
            icone='fas fa-chart-line',
            ordem=4,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Relatórios'))

        # ===========================================
        # MÓDULO CONTAS A RECEBER
        # ===========================================
        modulo_receber = Modulo.objects.create(
            nome='Contas a Receber',
            descricao='Módulo de gestão de contas a receber',
            icone='fas fa-hand-holding-usd',
            ordem=4,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Módulo criado: {modulo_receber.nome}'))

        Menu.objects.create(
            modulo=modulo_receber,
            nome='Dashboard',
            descricao='Dashboard de contas a receber',
            url='/contas-receber/',
            icone='fas fa-tachometer-alt',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Dashboard'))

        Menu.objects.create(
            modulo=modulo_receber,
            nome='Contas a Receber',
            descricao='Gestão de contas a receber',
            url='/contas-receber/contas/',
            icone='fas fa-file-invoice-dollar',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Contas a Receber'))

        Menu.objects.create(
            modulo=modulo_receber,
            nome='Clientes',
            descricao='Gestão de clientes',
            url='/contas-receber/clientes/',
            icone='fas fa-users',
            ordem=3,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Clientes'))

        Menu.objects.create(
            modulo=modulo_receber,
            nome='Créditos',
            descricao='Gestão de créditos de clientes',
            url='/contas-receber/creditos/',
            icone='fas fa-gift',
            ordem=4,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Créditos'))

        Menu.objects.create(
            modulo=modulo_receber,
            nome='Relatórios',
            descricao='Relatórios de contas a receber',
            url='/contas-receber/relatorios/',
            icone='fas fa-chart-bar',
            ordem=5,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Relatórios'))

        # ===========================================
        # MÓDULO IMPORTAÇÕES
        # ===========================================
        modulo_importacoes = Modulo.objects.create(
            nome='Importações',
            descricao='Módulo de importação de dados',
            icone='fas fa-download',
            ordem=5,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Módulo criado: {modulo_importacoes.nome}'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Dashboard',
            descricao='Dashboard de importações',
            url='/importacoes/dashboard/',
            icone='fas fa-tachometer-alt',
            ordem=1,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Dashboard'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Configurar Firebird',
            descricao='Configuração de conexão Firebird',
            url='/importacoes/configurar-firebird/',
            icone='fas fa-cog',
            ordem=2,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Configurar Firebird'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Cadastro Geral',
            descricao='Importação de cadastro geral',
            url='/importacoes/cadastro-geral/',
            icone='fas fa-users',
            ordem=3,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Cadastro Geral'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Notas Fiscais',
            descricao='Importação de notas fiscais',
            url='/importacoes/notas-fiscais/',
            icone='fas fa-file-invoice',
            ordem=4,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Notas Fiscais'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Parcelas',
            descricao='Importação de parcelas',
            url='/importacoes/parcelas/',
            icone='fas fa-money-bill-wave',
            ordem=5,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Parcelas'))

        Menu.objects.create(
            modulo=modulo_importacoes,
            nome='Histórico de Importações',
            descricao='Visualizar logs de importações',
            url='/importacoes/logs/',
            icone='fas fa-history',
            ordem=6,
            ativo=True
        )
        self.stdout.write(self.style.SUCCESS(f'  ✓ Menu criado: Histórico de Importações'))

        self.stdout.write(self.style.SUCCESS('\n✅ Dados iniciais criados com sucesso!'))
        self.stdout.write(self.style.WARNING('\n⚠ Não esqueça de atribuir permissões aos usuários no admin!'))

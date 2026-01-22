"""
Comando de gerenciamento para atualizar configuração do Firebird
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Atualiza a configuração do Firebird com o caminho correto do banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, help='Caminho do banco de dados')
        parser.add_argument('--host', type=str, help='IP ou hostname')
        parser.add_argument('--port', type=int, help='Porta')
        parser.add_argument('--user', type=str, help='Usuário')
        parser.add_argument('--password', type=str, help='Senha')

    def handle(self, *args, **options):
        from importacoes.models import ConfiguracaoFirebird
        
        config = ConfiguracaoFirebird.get_config()
        alteracoes = []
        
        if options.get('database'):
            config.database = options['database']
            alteracoes.append(f"Database: {options['database']}")
        
        if options.get('host'):
            config.host = options['host']
            alteracoes.append(f"Host: {options['host']}")
        
        if options.get('port'):
            config.port = options['port']
            alteracoes.append(f"Port: {options['port']}")
        
        if options.get('user'):
            config.user = options['user']
            alteracoes.append(f"User: {options['user']}")
        
        if options.get('password'):
            config.password = options['password']
            alteracoes.append(f"Password: ********")
        
        if alteracoes:
            config.save()
            self.stdout.write(self.style.SUCCESS('✅ Configuração atualizada:'))
            for alt in alteracoes:
                self.stdout.write(f'   {alt}')
        else:
            self.stdout.write(self.style.WARNING('⚠️ Nenhuma alteração especificada'))
        
        self.stdout.write('\n📋 Configuração atual:')
        self.stdout.write(f'   Host: {config.host}')
        self.stdout.write(f'   Porta: {config.port}')
        self.stdout.write(f'   Banco: {config.database}')
        self.stdout.write(f'   Usuário: {config.user}')

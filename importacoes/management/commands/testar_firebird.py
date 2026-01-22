"""
Comando de gerenciamento para testar conexão com Firebird
"""
from django.core.management.base import BaseCommand
import sys


class Command(BaseCommand):
    help = 'Testa a conexão com o Firebird e exibe informações de diagnóstico'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 80))
        self.stdout.write(self.style.HTTP_INFO('TESTE DE CONEXÃO FIREBIRD'))
        self.stdout.write(self.style.HTTP_INFO('=' * 80))
        
        # Testar import do fdb
        self.stdout.write('\n📦 VERIFICANDO BIBLIOTECA FDB...')
        try:
            import fdb
            self.stdout.write(self.style.SUCCESS(f'✅ FDB instalado com sucesso!'))
            self.stdout.write(f'   Versão: {getattr(fdb, "__version__", "desconhecida")}')
            self.stdout.write(f'   Localização: {fdb.__file__}')
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'❌ FDB não encontrado: {e}'))
            self.stdout.write(self.style.WARNING('\n🔧 Instale com: pip install fdb'))
            self.stdout.write(f'\n   Python em uso: {sys.executable}')
            self.stdout.write(f'   Python version: {sys.version}')
            return
        
        # Importar configuração
        self.stdout.write('\n⚙️  CARREGANDO CONFIGURAÇÃO...')
        from importacoes.models import ConfiguracaoFirebird
        config = ConfiguracaoFirebird.get_config()
        
        self.stdout.write(f'   Host: {config.host}')
        self.stdout.write(f'   Porta: {config.port}')
        self.stdout.write(f'   Banco: {config.database}')
        self.stdout.write(f'   Usuário: {config.user}')
        self.stdout.write(f'   Senha: {"*" * len(config.password) if config.password else "(vazia)"}')
        
        # Testar conexão
        self.stdout.write('\n🔌 TESTANDO CONEXÃO...')
        try:
            conn = fdb.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.user,
                password=config.password,
                charset='UTF8'
            )
            
            self.stdout.write(self.style.SUCCESS('✅ CONEXÃO ESTABELECIDA COM SUCESSO!'))
            self.stdout.write(f'   Server Version: {conn.server_version}')
            
            # Testar query
            self.stdout.write('\n🔍 TESTANDO QUERY...')
            cursor = conn.cursor()
            cursor.execute("SELECT FIRST 1 * FROM RDB$DATABASE")
            result = cursor.fetchone()
            cursor.close()
            
            self.stdout.write(self.style.SUCCESS('✅ QUERY EXECUTADA COM SUCESSO!'))
            
            conn.close()
            self.stdout.write('\n' + self.style.SUCCESS('=' * 80))
            self.stdout.write(self.style.SUCCESS('TESTE CONCLUÍDO COM SUCESSO!'))
            self.stdout.write(self.style.SUCCESS('=' * 80))
            
        except fdb.DatabaseError as e:
            self.stdout.write(self.style.ERROR('\n❌ ERRO DE BANCO DE DADOS:'))
            self.stdout.write(f'   Mensagem: {str(e)}')
            self.stdout.write(f'   SQL State: {getattr(e, "sqlstate", "N/A")}')
            self.stdout.write(f'   GDSCODE: {getattr(e, "gds_codes", "N/A")}')
            
            self.stdout.write(self.style.WARNING('\n📋 VERIFICAÇÕES SUGERIDAS:'))
            self.stdout.write('   1. Verifique se o IP/Host está correto e acessível')
            self.stdout.write('   2. Confirme se a porta 3050 está aberta')
            self.stdout.write('   3. Verifique se o caminho do banco está correto')
            self.stdout.write('   4. Confirme usuário e senha')
            self.stdout.write('   5. Verifique se o Firebird Server está rodando')
            self.stdout.write(f'   6. Teste ping: ping {config.host}')
            self.stdout.write(f'   7. Teste porta: telnet {config.host} {config.port}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERRO GERAL: {type(e).__name__}'))
            self.stdout.write(f'   Mensagem: {str(e)}')
            
            import traceback
            self.stdout.write('\n📋 STACK TRACE:')
            self.stdout.write(traceback.format_exc())

"""
Comando de gerenciamento para testar importação com debug detalhado
"""
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import sys
from io import StringIO


class Command(BaseCommand):
    help = 'Testa importação de cadastros com debug detalhado'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('=' * 80))
        self.stdout.write(self.style.HTTP_INFO('TESTE DE IMPORTAÇÃO - DEBUG DETALHADO'))
        self.stdout.write(self.style.HTTP_INFO('=' * 80))
        
        # Data de teste (últimos 7 dias)
        data_final = datetime.now().date()
        data_inicial = data_final - timedelta(days=7)
        
        self.stdout.write(f'\n📅 Período de teste: {data_inicial} até {data_final}')
        
        # Testar conexão primeiro
        self.stdout.write('\n🔌 TESTANDO CONEXÃO...')
        from importacoes.firebird_utils import FirebirdConnector
        
        connector = FirebirdConnector()
        if not connector.conectar():
            self.stdout.write(self.style.ERROR('❌ Falha na conexão. Abortando teste.'))
            return
        
        # Capturar output
        old_stdout = sys.stdout
        sys.stdout = captured = StringIO()
        
        try:
            # Testar query de cadastros
            self.stdout = old_stdout
            self.stdout.write('\n🔍 TESTANDO QUERY DE CADASTROS...')
            sys.stdout = captured
            
            sql = f"""
                SELECT FIRST 5 * FROM CADASTRO 
                WHERE DATA_CADASTRO BETWEEN '{data_inicial.strftime('%Y-%m-%d')}' 
                AND '{data_final.strftime('%Y-%m-%d')}'
            """
            
            sys.stdout = old_stdout
            self.stdout.write(f'SQL: {sql}')
            sys.stdout = captured
            
            colunas, resultados = connector.executar_query(sql)
            
            sys.stdout = old_stdout
            
            if colunas is None:
                self.stdout.write(self.style.ERROR('❌ Erro ao executar query'))
                self.stdout.write(f'\nOutput capturado:\n{captured.getvalue()}')
                return
            
            self.stdout.write(self.style.SUCCESS(f'✅ Query executada com sucesso!'))
            self.stdout.write(f'   Colunas encontradas: {len(colunas)}')
            self.stdout.write(f'   Registros retornados: {len(resultados) if resultados else 0}')
            
            if colunas:
                self.stdout.write(f'\n📋 Colunas da tabela CADASTRO:')
                for i, col in enumerate(colunas, 1):
                    self.stdout.write(f'   {i}. {col}')
            
            if resultados:
                self.stdout.write(f'\n📊 Primeiro registro (exemplo):')
                primeiro = dict(zip(colunas, resultados[0]))
                for k, v in list(primeiro.items())[:10]:  # Mostrar apenas primeiros 10 campos
                    self.stdout.write(f'   {k}: {v}')
            else:
                self.stdout.write(self.style.WARNING('\n⚠️ Nenhum registro encontrado no período'))
            
            # Testar importação real
            self.stdout.write('\n\n🚀 TESTANDO IMPORTAÇÃO REAL...')
            
            from importacoes.models import ImportacaoLog
            from django.contrib.auth.models import User
            
            # Pegar primeiro usuário admin
            user = User.objects.filter(is_superuser=True).first()
            
            log = ImportacaoLog.objects.create(
                tipo='cadastro',
                status='em_progresso',
                usuario=user,
                data_inicial_filtro=data_inicial,
                data_final_filtro=data_final,
            )
            
            self.stdout.write(f'   Log criado: #{log.id}')
            
            # Testar importação
            sys.stdout = captured
            connector.importar_cadastros(data_inicial, data_final, log)
            sys.stdout = old_stdout
            
            # Recarregar log
            log.refresh_from_db()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ IMPORTAÇÃO CONCLUÍDA!'))
            self.stdout.write(f'   Status: {log.status}')
            self.stdout.write(f'   Total: {log.total_registros}')
            self.stdout.write(f'   Criados: {log.registros_criados}')
            self.stdout.write(f'   Atualizados: {log.registros_atualizados}')
            self.stdout.write(f'   Erros: {log.registros_erro}')
            
            if log.mensagem:
                self.stdout.write(f'   Mensagem: {log.mensagem}')
            
            # Mostrar output capturado
            output = captured.getvalue()
            if output:
                self.stdout.write(f'\n📝 OUTPUT DO PROCESSO:')
                self.stdout.write(output)
            
        except Exception as e:
            sys.stdout = old_stdout
            self.stdout.write(self.style.ERROR(f'\n❌ ERRO NO TESTE: {type(e).__name__}'))
            self.stdout.write(f'   Mensagem: {str(e)}')
            
            import traceback
            self.stdout.write(f'\n📋 STACK TRACE:')
            self.stdout.write(traceback.format_exc())
            
            output = captured.getvalue()
            if output:
                self.stdout.write(f'\n📝 OUTPUT CAPTURADO:')
                self.stdout.write(output)
        
        finally:
            sys.stdout = old_stdout
            connector.desconectar()

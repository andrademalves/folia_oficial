from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db import transaction
from .models import ImportacaoLog, CadastroFutura, NotaFiscalFutura, ContaParcelaFutura

try:
    import fdb
    FDB_DISPONIVEL = True
    FDB_VERSAO = getattr(fdb, '__version__', 'desconhecida')
    FDB_ERRO_IMPORT = None
except ImportError as e:
    fdb = None
    FDB_DISPONIVEL = False
    FDB_VERSAO = None
    FDB_ERRO_IMPORT = str(e)
except Exception as e:
    fdb = None
    FDB_DISPONIVEL = False
    FDB_VERSAO = None
    FDB_ERRO_IMPORT = f"Erro ao importar fdb: {type(e).__name__}: {str(e)}"


class FirebirdConnector:
    """Gerenciador de conexão com banco Firebird do Futura"""
    
    def __init__(self):
        # Importar config dinamicamente para evitar circular import
        from .models import ConfiguracaoFirebird
        config = ConfiguracaoFirebird.get_config()
        
        self.host = config.host
        self.port = config.port
        self.database = config.database
        self.user = config.user
        self.password = config.password
        self.conn = None
    
    def conectar(self):
        """Estabelece conexão com Firebird"""
        # Verificar se fdb está disponível
        if not FDB_DISPONIVEL:
            erro_msg = f"❌ Biblioteca fdb não instalada. Instale com: pip install fdb\nErro: {FDB_ERRO_IMPORT}"
            print(erro_msg)
            raise ImportError(erro_msg)
        
        print("🔍 DEBUG - Tentando conectar ao Firebird...")
        print(f"   Host: {self.host}")
        print(f"   Port: {self.port}")
        print(f"   Database: {self.database}")
        print(f"   User: {self.user}")
        print(f"   Password: {'*' * len(self.password) if self.password else '(vazio)'}")
        print(f"   FDB Version: {FDB_VERSAO}")
        
        try:
            self.conn = fdb.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='UTF8'  # Importante para caracteres especiais
            )
            print("✅ Conectado ao Firebird com sucesso!")
            print(f"   Server Version: {self.conn.server_version}")
            return True
            
        except fdb.DatabaseError as e:
            print(f"\n❌ ERRO DE BANCO DE DADOS FIREBIRD:")
            print(f"   Tipo: DatabaseError")
            print(f"   Mensagem: {str(e)}")
            print(f"   SQL State: {getattr(e, 'sqlstate', 'N/A')}")
            print(f"   GDSCODE: {getattr(e, 'gds_codes', 'N/A')}")
            print("\n📋 VERIFICAÇÕES SUGERIDAS:")
            print("   1. Verifique se o IP/Host está correto e acessível")
            print("   2. Confirme se a porta 3050 está aberta no firewall")
            print("   3. Verifique se o caminho do banco de dados está correto")
            print("   4. Confirme usuário e senha")
            print("   5. Verifique se o serviço Firebird está rodando no servidor")
            print(f"   6. Teste ping: ping {self.host}")
            print(f"   7. Teste porta: telnet {self.host} {self.port}")
            return False
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL NA CONEXÃO:")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            import traceback
            print(f"\n   Stack Trace:\n{traceback.format_exc()}")
            return False
    
    def desconectar(self):
        """Fecha conexão com Firebird"""
        try:
            if self.conn:
                self.conn.close()
                print("✅ Desconectado do Firebird")
        except Exception as e:
            print(f"❌ Erro ao desconectar: {e}")
    
    def executar_query(self, sql):
        """Executa query e retorna resultados"""
        if not self.conn:
            print("❌ Sem conexão ativa com o banco")
            return None, None
            
        try:
            cursor = self.conn.cursor()
            print(f"🔍 Executando SQL: {sql[:100]}..." if len(sql) > 100 else f"🔍 Executando SQL: {sql}")
            cursor.execute(sql)
            colunas = [desc[0].lower() for desc in cursor.description]
            resultados = cursor.fetchall()
            cursor.close()
            print(f"✅ Query executada: {len(resultados)} registros retornados")
            return colunas, resultados
            
        except fdb.DatabaseError as e:
            print(f"❌ Erro de banco ao executar query:")
            print(f"   Mensagem: {str(e)}")
            print(f"   SQL: {sql}")
            return None, None
            
        except Exception as e:
            print(f"❌ Erro ao executar query: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            print(f"   SQL: {sql}")
            import traceback
            print(f"   Stack: {traceback.format_exc()}")
            return None, None
    
    def importar_cadastros(self, data_inicial, data_final, log):
        """Importa cadastros do Firebird"""
        print(f"📦 Iniciando importação de cadastros ({data_inicial} a {data_final})...")
        
        try:
            sql = f"""
                SELECT * FROM CADASTRO 
                WHERE DATA_CADASTRO BETWEEN '{data_inicial.strftime('%Y-%m-%d')}' AND '{data_final.strftime('%Y-%m-%d')}'
            """
            
            colunas, resultados = self.executar_query(sql)
            if not resultados:
                print("ℹ️ Nenhum cadastro encontrado no período")
                return
            
            print(f"🔍 {len(resultados)} cadastros encontrados")
            # Atualiza total imediatamente para permitir cálculo de progresso no frontend
            log.total_registros = len(resultados)
            log.save(update_fields=["total_registros"])
            
            criados = 0
            atualizados = 0
            erros = []
            
            with transaction.atomic():
                for row in resultados:
                    dados = dict(zip(colunas, row))
                    
                    try:
                        # Converter datas naive para aware (timezone) - apenas datetime, não date
                        from datetime import datetime as dt_class, date as date_class
                        
                        data_cadastro = dados.get('data_cadastro')
                        if data_cadastro and isinstance(data_cadastro, dt_class) and not isinstance(data_cadastro, str):
                            if data_cadastro.tzinfo is None:
                                data_cadastro = make_aware(data_cadastro)
                        
                        data_nascimento = dados.get('data_nascimento')
                        if data_nascimento and isinstance(data_nascimento, dt_class) and not isinstance(data_nascimento, str):
                            if data_nascimento.tzinfo is None:
                                data_nascimento = make_aware(data_nascimento)
                        
                        cadastro, created = CadastroFutura.objects.update_or_create(
                            id=dados.get('id'),
                            defaults={
                                'razao_social': dados.get('razao_social'),
                                'fantasia': dados.get('fantasia'),
                                'cnpj_cpf': dados.get('cnpj_cpf'),
                                'inscricao_rg': dados.get('inscricao_rg'),
                                'chk_cliente': dados.get('chk_cliente'),
                                'chk_fornecedor': dados.get('chk_fornecedor'),
                                'chk_funcionario': dados.get('chk_funcionario'),
                                'chk_transportadora': dados.get('chk_transportadora'),
                                'chk_empresa': dados.get('chk_empresa'),
                                'chk_vendedor': dados.get('chk_vendedor'),
                                'e_mail': dados.get('e_mail'),
                                'e_mail_alternativo': dados.get('e_mail_alternativo'),
                                'limite_compra_funcionario': dados.get('limite_compra_funcionario') or 0,
                                'limite_venda_valor': dados.get('limite_venda_valor') or 0,
                                'limite_desconto_percentual': dados.get('limite_desconto_percentual') or 0,
                                'fk_vendedor': dados.get('fk_vendedor'),
                                'fk_transportadora': dados.get('fk_transportadora'),
                                'fk_empresa': dados.get('fk_empresa'),
                                'data_cadastro': data_cadastro,
                                'data_nascimento': data_nascimento,
                                'status': dados.get('status'),
                                'observacao': dados.get('observacao'),
                                'importacao_log': log,
                            }
                        )
                        
                        if created:
                            criados += 1
                        else:
                            atualizados += 1
                    
                    except Exception as erro:
                        erros.append({
                            'id': dados.get('id'),
                            'razao_social': dados.get('razao_social'),
                            'erro': str(erro)
                        })
                    # Persistir progresso a cada 10 registros para feedback ao usuário
                    total_processado = criados + atualizados + len(erros)
                    if total_processado % 10 == 0 or total_processado == 1:
                        log.registros_criados = criados
                        log.registros_atualizados = atualizados
                        log.registros_erro = len(erros)
                        log.mensagem = f"Processando {total_processado} de {log.total_registros}"
                        log.save(update_fields=[
                            "registros_criados",
                            "registros_atualizados",
                            "registros_erro",
                            "mensagem",
                        ])
            
            log.total_registros = len(resultados)
            log.registros_criados = criados
            log.registros_atualizados = atualizados
            log.registros_erro = len(erros)
            log.erros_detalhe = erros
            log.save()
            
            print(f"✅ Importação concluída: {criados} criados, {atualizados} atualizados, {len(erros)} erros")
            
        except Exception as e:
            print(f"❌ Erro na importação de cadastros: {e}")
            log.mensagem = str(e)
            log.save()
    
    def importar_notas_fiscais(self, data_inicial, data_final, log):
        """Importa notas fiscais do Firebird"""
        print(f"📦 Iniciando importação de notas fiscais ({data_inicial} a {data_final})...")
        
        try:
            sql = f"""
                SELECT * FROM NOTA_FISCAL 
                WHERE DATA_EMISSAO BETWEEN '{data_inicial.strftime('%Y-%m-%d')}' AND '{data_final.strftime('%Y-%m-%d')}'
            """
            
            colunas, resultados = self.executar_query(sql)
            if not resultados:
                print("ℹ️ Nenhuma nota fiscal encontrada no período")
                return
            
            print(f"🔍 {len(resultados)} notas fiscais encontradas")
            log.total_registros = len(resultados)
            log.save(update_fields=["total_registros"])
            
            criadas = 0
            atualizadas = 0
            erros = []
            
            with transaction.atomic():
                for row in resultados:
                    dados = dict(zip(colunas, row))
                    
                    try:
                        nf, created = NotaFiscalFutura.objects.update_or_create(
                            id=dados.get('id'),
                            defaults={
                                'nro_nota': dados.get('nro_nota'),
                                'serie': dados.get('serie'),
                                'fk_empresa': dados.get('fk_empresa'),
                                'fk_cadastro': dados.get('fk_cadastro'),
                                'fk_pedido': dados.get('fk_pedido'),
                                'fk_transportadora': dados.get('fk_transportadora'),
                                'fk_vendedor': dados.get('fk_vendedor'),
                                'data_emissao': dados.get('data_emissao'),
                                'data_saida_entrada': dados.get('data_saida_entrada'),
                                'data_competencia': dados.get('data_competencia'),
                                'data_hora_emissao': dados.get('data_hora_emissao'),
                                'total_produto': dados.get('total_produto') or 0,
                                'total_frete': dados.get('total_frete') or 0,
                                'total_desconto': dados.get('total_desconto') or 0,
                                'total_acrescimo': dados.get('total_acrescimo') or 0,
                                'total_nota': dados.get('total_nota') or 0,
                                'total_icms_valor': dados.get('total_icms_valor') or 0,
                                'total_ipi_valor': dados.get('total_ipi_valor') or 0,
                                'total_tributos_valor': dados.get('total_tributos_valor') or 0,
                                'quantidade': dados.get('quantidade'),
                                'especie': dados.get('especie'),
                                'placa': dados.get('placa'),
                                'status': dados.get('status'),
                                'entrada_saida': dados.get('entrada_saida'),
                                'cnpj_cpf_cliente': dados.get('cnpj_cpf_cliente'),
                                'observacao_1': dados.get('observacao_1'),
                                'observacao_2': dados.get('observacao_2'),
                                'importacao_log': log,
                            }
                        )
                        
                        if created:
                            criadas += 1
                        else:
                            atualizadas += 1
                    
                    except Exception as erro:
                        erros.append({
                            'id': dados.get('id'),
                            'nro_nota': dados.get('nro_nota'),
                            'erro': str(erro)
                        })
                    total_processado = criadas + atualizadas + len(erros)
                    if total_processado % 10 == 0 or total_processado == 1:
                        log.registros_criados = criadas
                        log.registros_atualizados = atualizadas
                        log.registros_erro = len(erros)
                        log.mensagem = f"Processando {total_processado} de {log.total_registros}"
                        log.save(update_fields=[
                            "registros_criados",
                            "registros_atualizados",
                            "registros_erro",
                            "mensagem",
                        ])
            
            log.total_registros = len(resultados)
            log.registros_criados = criadas
            log.registros_atualizados = atualizadas
            log.registros_erro = len(erros)
            log.erros_detalhe = erros
            log.save()
            
            print(f"✅ Importação concluída: {criadas} criadas, {atualizadas} atualizadas, {len(erros)} erros")
            
        except Exception as e:
            print(f"❌ Erro na importação de notas fiscais: {e}")
            log.mensagem = str(e)
            log.save()
    
    def importar_parcelas(self, data_inicial, data_final, log):
        """Importa parcelas de contas do Firebird"""
        print(f"📦 Iniciando importação de parcelas ({data_inicial} a {data_final})...")
        
        try:
            sql = f"""
                SELECT * FROM CONTA_PARCELA 
                WHERE DATA_VENCIMENTO BETWEEN '{data_inicial.strftime('%Y-%m-%d')}' AND '{data_final.strftime('%Y-%m-%d')}'
            """
            
            colunas, resultados = self.executar_query(sql)
            if not resultados:
                print("ℹ️ Nenhuma parcela encontrada no período")
                return
            
            print(f"🔍 {len(resultados)} parcelas encontradas")
            log.total_registros = len(resultados)
            log.save(update_fields=["total_registros"])
            
            criadas = 0
            atualizadas = 0
            erros = []
            
            with transaction.atomic():
                for row in resultados:
                    dados = dict(zip(colunas, row))
                    
                    try:
                        parcela, created = ContaParcelaFutura.objects.update_or_create(
                            id=dados.get('id'),
                            defaults={
                                'fk_conta': dados.get('fk_conta'),
                                'fk_nota_fiscal': dados.get('fk_nota_fiscal_servico'),
                                'documento': dados.get('documento'),
                                'nosso_numero': dados.get('nosso_numero'),
                                'data_vencimento': dados.get('data_vencimento'),
                                'valor_parcela': dados.get('valor_parcela') or 0,
                                'valor_pago': dados.get('valor_pago') or 0,
                                'valor_desconto': dados.get('valor_desconto') or 0,
                                'valor_multa': dados.get('valor_multa') or 0,
                                'valor_juros': dados.get('valor_juros') or 0,
                                'status': dados.get('status'),
                                'dias_atraso': dados.get('dias_atraso'),
                                'boleto_codigo_barras': dados.get('boleto_codigo_barras'),
                                'boleto_linha_digitavel': dados.get('boleto_linha_digitavel'),
                                'boleto_qrcode_pix': dados.get('boleto_qrcode_pix'),
                                'importacao_log': log,
                            }
                        )
                        
                        if created:
                            criadas += 1
                        else:
                            atualizadas += 1
                    
                    except Exception as erro:
                        erros.append({
                            'id': dados.get('id'),
                            'documento': dados.get('documento'),
                            'erro': str(erro)
                        })
                    total_processado = criadas + atualizadas + len(erros)
                    if total_processado % 10 == 0 or total_processado == 1:
                        log.registros_criados = criadas
                        log.registros_atualizados = atualizadas
                        log.registros_erro = len(erros)
                        log.mensagem = f"Processando {total_processado} de {log.total_registros}"
                        log.save(update_fields=[
                            "registros_criados",
                            "registros_atualizados",
                            "registros_erro",
                            "mensagem",
                        ])
            
            log.total_registros = len(resultados)
            log.registros_criados = criadas
            log.registros_atualizados = atualizadas
            log.registros_erro = len(erros)
            log.erros_detalhe = erros
            log.save()
            
            print(f"✅ Importação concluída: {criadas} criadas, {atualizadas} atualizadas, {len(erros)} erros")
            
        except Exception as e:
            print(f"❌ Erro na importação de parcelas: {e}")
            log.mensagem = str(e)
            log.save()


def executar_importacao(tipo, data_inicial, data_final, usuario=None, log: ImportacaoLog | None = None):
    """
    Função wrapper para executar importação completa
    
    Args:
        tipo: 'cadastro', 'nota_fiscal' ou 'conta_parcela'
        data_inicial: data inicial do período
        data_final: data final do período
        usuario: usuário que executou a importação
    
    Returns:
        ImportacaoLog: log da importação
    """
    
    # Criar ou usar log existente
    if log is None:
        log = ImportacaoLog.objects.create(
            tipo=tipo,
            status='em_progresso',
            usuario=usuario,
            data_inicial_filtro=data_inicial,
            data_final_filtro=data_final,
        )
    else:
        # garantir que esteja com status correto e datas
        log.status = 'em_progresso'
        log.usuario = usuario or log.usuario
        log.data_inicial_filtro = data_inicial
        log.data_final_filtro = data_final
        log.save(update_fields=[
            'status', 'usuario', 'data_inicial_filtro', 'data_final_filtro'
        ])
    
    # Conectar e importar
    connector = FirebirdConnector()
    
    try:
        if not connector.conectar():
            log.status = 'erro'
            log.mensagem = 'Falha ao conectar ao Firebird'
            log.save()
            return log
        
        if tipo == 'cadastro':
            connector.importar_cadastros(data_inicial, data_final, log)
        elif tipo == 'nota_fiscal':
            connector.importar_notas_fiscais(data_inicial, data_final, log)
        elif tipo == 'conta_parcela':
            connector.importar_parcelas(data_inicial, data_final, log)
        
        log.status = 'concluida'
        log.data_fim = make_aware(datetime.now())
        log.save()
        
        return log
    
    except Exception as e:
        print(f"❌ Erro geral na importação: {e}")
        log.status = 'erro'
        log.mensagem = str(e)
        log.save()
        return log
    
    finally:
        connector.desconectar()

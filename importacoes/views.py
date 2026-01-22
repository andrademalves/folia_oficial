from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from usuarios.decorators import permissao_menu_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.dateparse import parse_date
import threading
from .models import ImportacaoLog, CadastroFutura, NotaFiscalFutura, ContaParcelaFutura, ConfiguracaoFirebird
from .forms import ImportacaoForm, FiltroImportacaoForm, ConfiguracaoFirebirdForm
from .firebird_utils import executar_importacao, FirebirdConnector, FDB_DISPONIVEL, FDB_VERSAO


@login_required
@permissao_menu_required('/importacoes/', 'visualizar')
def dashboard_importacoes(request):
    """
    Dashboard principal do módulo de importações
    """
    # Últimas importações
    ultimas_importacoes = ImportacaoLog.objects.all()[:10]
    
    # Estatísticas
    total_cadastros = CadastroFutura.objects.count()
    total_notas = NotaFiscalFutura.objects.count()
    total_parcelas = ContaParcelaFutura.objects.count()
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'ultimas_importacoes': ultimas_importacoes,
        'total_cadastros': total_cadastros,
        'total_notas': total_notas,
        'total_parcelas': total_parcelas,
    }
    return render(request, 'importacoes/dashboard.html', context)


@login_required
@permissao_menu_required('/importacoes/cadastro-geral/', 'visualizar')
def importar_cadastro_geral(request):
    """
    Importação de cadastro geral do sistema Futura
    """
    import traceback
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = ImportacaoForm(request.POST)
        if form.is_valid():
            try:
                logger.info(f"Iniciando importação de cadastros - Data inicial: {form.cleaned_data['data_inicial']}, Data final: {form.cleaned_data['data_final']}")
                
                log = executar_importacao(
                    tipo='cadastro',
                    data_inicial=form.cleaned_data['data_inicial'],
                    data_final=form.cleaned_data['data_final'],
                    usuario=request.user
                )
                
                logger.info(f"Importação concluída - Status: {log.status}")
                
                if log.status == 'erro':
                    messages.error(
                        request,
                        f"❌ Erro na importação: {log.mensagem}\n\n"
                        f"Detalhes: Verifique os logs para mais informações."
                    )
                else:
                    messages.success(
                        request, 
                        f"✅ Importação concluída! {log.registros_criados} criados, "
                        f"{log.registros_atualizados} atualizados, {log.registros_erro} erros."
                    )
                return redirect('importacoes:logs')
            
            except Exception as e:
                error_trace = traceback.format_exc()
                logger.error(f"Erro na importação: {str(e)}\n{error_trace}")
                messages.error(
                    request, 
                    f"❌ Erro crítico na importação:\n"
                    f"Tipo: {type(e).__name__}\n"
                    f"Mensagem: {str(e)}\n\n"
                    f"Stack trace completo no console do servidor."
                )
    else:
        form = ImportacaoForm(initial={'tipo': 'cadastro'})
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'form': form,
        'titulo': 'Importar Cadastros'
    }
    return render(request, 'importacoes/cadastro_geral.html', context)


@login_required
@permissao_menu_required('/importacoes/notas-fiscais/', 'visualizar')
def importar_notas_fiscais(request):
    """
    Importação de notas fiscais do sistema Futura
    """
    if request.method == 'POST':
        form = ImportacaoForm(request.POST)
        if form.is_valid():
            try:
                log = executar_importacao(
                    tipo='nota_fiscal',
                    data_inicial=form.cleaned_data['data_inicial'],
                    data_final=form.cleaned_data['data_final'],
                    usuario=request.user
                )
                
                messages.success(
                    request,
                    f"✅ Importação concluída! {log.registros_criados} criadas, "
                    f"{log.registros_atualizados} atualizadas, {log.registros_erro} erros."
                )
                return redirect('importacoes:logs')
            
            except Exception as e:
                messages.error(request, f"❌ Erro na importação: {str(e)}")
    else:
        form = ImportacaoForm(initial={'tipo': 'nota_fiscal'})
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'form': form,
        'titulo': 'Importar Notas Fiscais'
    }
    return render(request, 'importacoes/notas_fiscais.html', context)


@login_required
@permissao_menu_required('/importacoes/parcelas/', 'visualizar')
def importar_parcelas(request):
    """
    Importação de parcelas de contas do sistema Futura
    """
    if request.method == 'POST':
        form = ImportacaoForm(request.POST)
        if form.is_valid():
            try:
                log = executar_importacao(
                    tipo='conta_parcela',
                    data_inicial=form.cleaned_data['data_inicial'],
                    data_final=form.cleaned_data['data_final'],
                    usuario=request.user
                )
                
                messages.success(
                    request,
                    f"✅ Importação concluída! {log.registros_criados} criadas, "
                    f"{log.registros_atualizados} atualizadas, {log.registros_erro} erros."
                )
                return redirect('importacoes:logs')
            
            except Exception as e:
                messages.error(request, f"❌ Erro na importação: {str(e)}")
    else:
        form = ImportacaoForm(initial={'tipo': 'conta_parcela'})
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'form': form,
        'titulo': 'Importar Parcelas'
    }
    return render(request, 'importacoes/parcelas.html', context)


@login_required
@require_POST
@permissao_menu_required('/importacoes/', 'visualizar')
def api_iniciar_importacao(request):
    """Inicia a importação em background e retorna o ID do log"""
    tipo = request.POST.get('tipo')
    data_inicial = parse_date(request.POST.get('data_inicial'))
    data_final = parse_date(request.POST.get('data_final'))

    if not tipo or not data_inicial or not data_final:
        return JsonResponse({'ok': False, 'erro': 'Parâmetros inválidos'}, status=400)

    # cria log prévio
    log = ImportacaoLog.objects.create(
        tipo=tipo,
        status='em_progresso',
        usuario=request.user,
        data_inicial_filtro=data_inicial,
        data_final_filtro=data_final,
    )

    # função alvo do thread
    def _run_import():
        try:
            executar_importacao(tipo=tipo, data_inicial=data_inicial, data_final=data_final, usuario=request.user, log=log)
        except Exception as e:
            log.status = 'erro'
            log.mensagem = str(e)
            log.save()

    t = threading.Thread(target=_run_import, daemon=True)
    t.start()

    return JsonResponse({'ok': True, 'log_id': log.id})


@login_required
@require_GET
@permissao_menu_required('/importacoes/', 'visualizar')
def api_status_importacao(request, pk: int):
    """Retorna status e progresso da importação"""
    log = get_object_or_404(ImportacaoLog, pk=pk)
    processados = log.registros_criados + log.registros_atualizados + log.registros_erro
    total = log.total_registros or 0
    percent = 0
    if total > 0:
        percent = int(min(100, round((processados / total) * 100)))
    return JsonResponse({
        'ok': True,
        'status': log.status,
        'mensagem': log.mensagem or '',
        'log_id': log.id,
        'total': total,
        'processados': processados,
        'criados': log.registros_criados,
        'atualizados': log.registros_atualizados,
        'erros': log.registros_erro,
        'percent': percent,
        'concluida': log.status == 'concluida',
    })


@login_required
@permissao_menu_required('/importacoes/logs/', 'visualizar')
def logs_importacao(request):
    """
    Lista de logs de importação
    """
    logs = ImportacaoLog.objects.all()
    
    # Filtros
    if request.method == 'POST':
        form = FiltroImportacaoForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('tipo'):
                logs = logs.filter(tipo=form.cleaned_data['tipo'])
            
            if form.cleaned_data.get('status'):
                logs = logs.filter(status=form.cleaned_data['status'])
            
            if form.cleaned_data.get('data_inicio'):
                logs = logs.filter(data_inicio__date__gte=form.cleaned_data['data_inicio'])
            
            if form.cleaned_data.get('data_fim'):
                logs = logs.filter(data_inicio__date__lte=form.cleaned_data['data_fim'])
    else:
        form = FiltroImportacaoForm()
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'logs': logs,
        'form': form,
    }
    return render(request, 'importacoes/logs.html', context)


@login_required
@permissao_menu_required('/importacoes/logs/', 'visualizar')
def detalhe_log(request, pk):
    """
    Detalhe de um log de importação
    """
    log = get_object_or_404(ImportacaoLog, pk=pk)
    
    # Buscar registros relacionados
    cadastros = None
    notas = None
    parcelas = None
    
    if log.tipo == 'cadastro':
        cadastros = CadastroFutura.objects.filter(importacao_log=log)
    elif log.tipo == 'nota_fiscal':
        notas = NotaFiscalFutura.objects.filter(importacao_log=log)
    elif log.tipo == 'conta_parcela':
        parcelas = ContaParcelaFutura.objects.filter(importacao_log=log)
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'log': log,
        'cadastros': cadastros,
        'notas': notas,
        'parcelas': parcelas,
    }
    return render(request, 'importacoes/detalhe_log.html', context)


@login_required
@permissao_menu_required('/importacoes/', 'visualizar')
def configurar_firebird(request):
    """
    Página para configurar credenciais de conexão ao Firebird
    """
    config = ConfiguracaoFirebird.get_config()
    
    if request.method == 'POST':
        form = ConfiguracaoFirebirdForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Configurações do Firebird atualizadas com sucesso!')
            return redirect('importacoes:dashboard')
    else:
        form = ConfiguracaoFirebirdForm(instance=config)
    
    context = {
        'form': form,
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'config': config,
        'fdb_disponivel': FDB_DISPONIVEL,
        'fdb_versao': FDB_VERSAO if FDB_DISPONIVEL else None,
    }
    return render(request, 'importacoes/configurar_firebird.html', context)


@login_required
@permissao_menu_required('/importacoes/', 'visualizar')
def testar_conexao_firebird(request):
    """
    Testa a conexão com o Firebird e retorna resultado detalhado
    """
    import sys
    from io import StringIO
    
    config = ConfiguracaoFirebird.get_config()
    output_log = ""
    
    # Capturar output do console
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        connector = FirebirdConnector()
        sucesso = connector.conectar()
        
        if sucesso:
            # Tentar executar query simples
            colunas, resultados = connector.executar_query("SELECT FIRST 1 * FROM RDB$DATABASE")
            if resultados is not None:
                messages.success(request, '✅ Conexão com Firebird estabelecida com sucesso!')
            else:
                messages.warning(request, '⚠️ Conectado mas erro ao executar query de teste')
            connector.desconectar()
        else:
            messages.error(request, '❌ Falha ao conectar no Firebird. Veja os detalhes abaixo.')
    
    except Exception as e:
        messages.error(request, f'❌ Erro ao testar conexão: {str(e)}')
    
    finally:
        # Restaurar stdout
        sys.stdout = old_stdout
        output_log = captured_output.getvalue()
    
    context = {
        'hide_sidebar': True,
        'modulo_ativo': 'importacoes',
        'output_log': output_log,
        'config': config,
        'fdb_disponivel': FDB_DISPONIVEL,
        'fdb_versao': FDB_VERSAO if FDB_DISPONIVEL else None,
    }
    return render(request, 'importacoes/teste_conexao.html', context)

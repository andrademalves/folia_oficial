from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
from decimal import Decimal
from .models import ConfiguracaoBancaria, Boleto, RemessaCNAB
from contas_receber.models import Parcela, Cliente
from .utils.codigo_barras import gerar_codigo_barras, gerar_linha_digitavel
from .utils.cnab240_novo import GeradorCNAB240Caixa
from .utils.gerar_pdf import gerar_pdf_boleto
from usuarios.decorators import verificar_permissao_menu, verificar_permissao_acao
from .forms import ConfiguracaoBancariaForm


@login_required
@verificar_permissao_menu('/boletos/')
def dashboard_boletos(request):
    """Dashboard do módulo de boletos"""
    # Estatísticas
    total_boletos = Boleto.objects.count()
    boletos_pendentes = Boleto.objects.filter(status='PENDENTE').count()
    boletos_emitidos = Boleto.objects.filter(status='EMITIDO').count()
    boletos_registrados = Boleto.objects.filter(status='REGISTRADO').count()
    boletos_pagos = Boleto.objects.filter(status='PAGO').count()
    
    # Boletos vencendo nos próximos 7 dias
    hoje = timezone.now().date()
    data_limite = hoje + timedelta(days=7)
    boletos_vencendo = Boleto.objects.filter(
        data_vencimento__range=[hoje, data_limite],
        status__in=['EMITIDO', 'REGISTRADO']
    ).order_by('data_vencimento')[:10]
    
    # Boletos vencidos
    boletos_vencidos = Boleto.objects.filter(
        data_vencimento__lt=hoje,
        status__in=['EMITIDO', 'REGISTRADO']
    ).count()
    
    # Remessas recentes
    remessas_recentes = RemessaCNAB.objects.all().order_by('-data_geracao')[:5]
    
    # Configurações ativas
    configuracoes = ConfiguracaoBancaria.objects.filter(ativo=True)
    
    context = {
        'total_boletos': total_boletos,
        'boletos_pendentes': boletos_pendentes,
        'boletos_emitidos': boletos_emitidos,
        'boletos_registrados': boletos_registrados,
        'boletos_pagos': boletos_pagos,
        'boletos_vencendo': boletos_vencendo,
        'boletos_vencidos': boletos_vencidos,
        'remessas_recentes': remessas_recentes,
        'configuracoes': configuracoes,
        'hide_sidebar': True,  # Oculta sidebar do base.html
    }
    
    return render(request, 'boletos/dashboard.html', context)


@login_required
@verificar_permissao_menu('/boletos/boletos/')
def lista_boletos(request):
    """Lista todos os boletos com filtros"""
    boletos = Boleto.objects.select_related('configuracao', 'cliente', 'parcela').all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        boletos = boletos.filter(status=status)
    
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        boletos = boletos.filter(cliente_id=cliente_id)
    
    nosso_numero = request.GET.get('nosso_numero')
    if nosso_numero:
        boletos = boletos.filter(numero_documento__icontains=nosso_numero)
    
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')
    if data_ini and data_fim:
        boletos = boletos.filter(data_vencimento__range=[data_ini, data_fim])
    
    boletos = boletos.order_by('-data_vencimento')
    
    # Paginação
    paginator = Paginator(boletos, 20)  # 20 boletos por página
    page = request.GET.get('page', 1)
    
    try:
        boletos_pagina = paginator.page(page)
    except PageNotAnInteger:
        boletos_pagina = paginator.page(1)
    except EmptyPage:
        boletos_pagina = paginator.page(paginator.num_pages)
    
    # Buscar todos os clientes que possuem boletos
    clientes = Cliente.objects.filter(
        id__in=Boleto.objects.values_list('cliente_id', flat=True)
    ).distinct().order_by('nome')
    
    context = {
        'boletos': boletos_pagina,
        'clientes': clientes,
        'status_choices': Boleto.STATUS_CHOICES,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/lista_boletos.html', context)


@login_required
@verificar_permissao_acao('/boletos/boletos/', 'criar')
def selecionar_parcelas_boleto(request):
    """Seleciona parcelas para gerar boletos em lote"""
    # Busca parcelas pendentes que não têm boleto
    parcelas = Parcela.objects.filter(
        status_pagamento='pendente'
    ).exclude(
        id__in=Boleto.objects.values_list('parcela_id', flat=True)
    ).select_related('cliente', 'nota_fiscal')
    
    # Filtro por tipo (NF ou CARTEIRA)
    tipo_parcela = request.GET.get('tipo_parcela')
    if tipo_parcela:
        parcelas = parcelas.filter(tipo_parcela=tipo_parcela)
    
    # Filtro por cliente
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        parcelas = parcelas.filter(cliente_id=cliente_id)
    
    # Filtro por período de vencimento
    data_venc_ini = request.GET.get('data_venc_ini')
    data_venc_fim = request.GET.get('data_venc_fim')
    if data_venc_ini and data_venc_fim:
        parcelas = parcelas.filter(data_vencimento__range=[data_venc_ini, data_venc_fim])
    
    parcelas = parcelas.order_by('data_vencimento', 'cliente__nome')
    
    # Busca todos os clientes com parcelas pendentes
    clientes = Cliente.objects.filter(
        parcelas__status_pagamento='pendente'
    ).distinct().order_by('nome')
    
    # Configurações bancárias ativas
    configuracoes = ConfiguracaoBancaria.objects.filter(ativo=True)
    
    context = {
        'parcelas': parcelas,
        'clientes': clientes,
        'configuracoes': configuracoes,
        'tipo_parcela': tipo_parcela,
        'cliente_id': cliente_id,
        'data_venc_ini': data_venc_ini,
        'data_venc_fim': data_venc_fim,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/selecionar_parcelas.html', context)


@login_required
@verificar_permissao_acao('/boletos/boletos/', 'criar')
def gerar_boletos_lote(request):
    """Gera boletos em lote para as parcelas selecionadas"""
    if request.method != 'POST':
        return redirect('boletos:selecionar_parcelas_boleto')
    
    parcela_ids = request.POST.getlist('parcelas')
    config_id = request.POST.get('configuracao')
    
    if not parcela_ids:
        messages.error(request, 'Selecione pelo menos uma parcela.')
        return redirect('boletos:selecionar_parcelas_boleto')
    
    if not config_id:
        messages.error(request, 'Selecione uma configuração bancária.')
        return redirect('boletos:selecionar_parcelas_boleto')
    
    try:
        configuracao = ConfiguracaoBancaria.objects.get(id=config_id, ativo=True)
    except ConfiguracaoBancaria.DoesNotExist:
        messages.error(request, 'Configuração bancária inválida.')
        return redirect('boletos:selecionar_parcelas_boleto')
    
    # Gera boletos
    boletos_gerados = 0
    erros = []
    
    for parcela_id in parcela_ids:
        try:
            parcela = Parcela.objects.get(id=parcela_id, status_pagamento='pendente')
            
            # Verifica se já existe boleto
            if hasattr(parcela, 'boleto'):
                erros.append(f"Parcela {parcela.codigo_identificador} já possui boleto.")
                continue
            
            # Validações antes de gerar
            if not parcela.data_vencimento:
                erros.append(f"Parcela {parcela_id}: data de vencimento não informada.")
                continue
            
            if not parcela.valor or parcela.valor <= 0:
                erros.append(f"Parcela {parcela_id}: valor inválido.")
                continue
            
            # Gera o boleto
            boleto = Boleto.objects.create(
                configuracao=configuracao,
                cliente=parcela.cliente,
                parcela=parcela,
                numero_documento=str(parcela.codigo_identificador),  # Código identificador da parcela
                nosso_numero=configuracao.proximo_nosso_numero(),
                valor_documento=parcela.valor,
                data_emissao=timezone.now().date(),
                data_vencimento=parcela.data_vencimento,
                status='PENDENTE'
            )
            
            # Gera código de barras e linha digitável
            try:
                boleto.codigo_barras = gerar_codigo_barras(boleto)
                boleto.linha_digitavel = gerar_linha_digitavel(boleto.codigo_barras)
                boleto.status = 'EMITIDO'
                boleto.save()
                boletos_gerados += 1
            except Exception as e:
                boleto.delete()  # Remove o boleto criado se falhar
                erros.append(f"Erro ao gerar código de barras para parcela {parcela_id}: {str(e)}")
            
        except Parcela.DoesNotExist:
            erros.append(f"Parcela ID {parcela_id} não encontrada.")
        except Exception as e:
            erros.append(f"Erro ao gerar boleto para parcela {parcela_id}: {str(e)}")
    
    # Mensagens de resultado
    if boletos_gerados > 0:
        messages.success(request, f'{boletos_gerados} boleto(s) gerado(s) com sucesso!')
    
    if erros:
        for erro in erros:
            messages.warning(request, erro)
    
    return redirect('boletos:lista_boletos')


@login_required
@verificar_permissao_acao('/boletos/boletos/', 'criar')
def gerar_boleto_parcela(request, parcela_id):
    """Gera um boleto para uma parcela"""
    parcela = get_object_or_404(Parcela, id=parcela_id)
    
    # Verifica se já existe boleto para esta parcela
    if hasattr(parcela, 'boleto'):
        messages.warning(request, 'Já existe um boleto para esta parcela.')
        return redirect('boletos:detalhe_boleto', boleto_id=parcela.boleto.id)
    
    # Busca configuração ativa
    try:
        config = ConfiguracaoBancaria.objects.filter(ativo=True).first()
        if not config:
            messages.error(request, 'Nenhuma configuração bancária ativa encontrada.')
            return redirect('boletos:lista_boletos')
    except ConfiguracaoBancaria.DoesNotExist:
        messages.error(request, 'Configure os dados bancários antes de gerar boletos.')
        return redirect('boletos:lista_boletos')
    
    if request.method == 'POST':
        try:
            # Cria o boleto
            boleto = Boleto.objects.create(
                configuracao=config,
                parcela=parcela,
                cliente=parcela.nota_fiscal.cliente,
                numero_documento=str(parcela.codigo_identificador),  # Código identificador da parcela
                valor_documento=parcela.valor,
                data_emissao=timezone.now().date(),
                data_vencimento=parcela.data_vencimento,
                instrucao1=config.instrucao1,
                instrucao2=config.instrucao2,
                mensagem_sacador=f"Nota Fiscal {parcela.nota_fiscal.numero_nf} - Parcela {parcela.parcela}",
                status='EMITIDO'
            )
            
            messages.success(request, f'Boleto {boleto.nosso_numero} gerado com sucesso!')
            return redirect('boletos:detalhe_boleto', boleto_id=boleto.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao gerar boleto: {str(e)}')
    
    context = {
        'parcela': parcela,
        'config': config,
    }
    
    return render(request, 'boletos/gerar_boleto.html', context)


@login_required
@verificar_permissao_menu('/boletos/boletos/')
def detalhe_boleto(request, boleto_id):
    """Exibe detalhes de um boleto"""
    boleto = get_object_or_404(
        Boleto.objects.select_related('configuracao', 'cliente', 'parcela'),
        id=boleto_id
    )
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'boletos/detalhe_boleto.html', context)


@login_required
@verificar_permissao_menu('/boletos/boletos/')
def imprimir_boleto(request, boleto_id):
    """Gera o PDF do boleto para impressão"""
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    try:
        # Gera o PDF
        pdf_buffer = gerar_pdf_boleto(boleto)
        
        # Retorna o PDF como resposta
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="boleto_{boleto.nosso_numero}.pdf"'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect('boletos:detalhe_boleto', boleto_id=boleto_id)


@login_required
@verificar_permissao_menu('/boletos/remessas/')
def gerar_remessa_cnab(request):
    """Gera arquivo de remessa CNAB 240"""
    if request.method == 'POST':
        boleto_ids = request.POST.getlist('boletos')
        
        if not boleto_ids:
            messages.error(request, 'Selecione pelo menos um boleto.')
            return redirect('boletos:lista_boletos')
        
        boletos = Boleto.objects.filter(id__in=boleto_ids, status='EMITIDO')
        
        if not boletos.exists():
            messages.error(request, 'Nenhum boleto válido selecionado.')
            return redirect('boletos:lista_boletos')
        
        try:
            # Busca configuração
            config = boletos.first().configuracao
            
            # Gera o arquivo CNAB usando o novo gerador profissional
            gerador = GeradorCNAB240Caixa(config)
            conteudo_cnab = gerador.gerar_remessa(list(boletos))
            
            # O novo gerador já valida automaticamente durante a geração
            # Validação adicional opcional:
            if not conteudo_cnab or len(conteudo_cnab) < 480:  # Mínimo: header + trailer arquivo
                messages.error(request, 'Arquivo CNAB gerado está vazio ou incompleto.')
                return redirect('boletos:lista_boletos')
            
            # Cria o registro de remessa
            data_hora = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f'CB{config.codigo_beneficiario.zfill(7)}_{data_hora}.REM'
            
            remessa = RemessaCNAB.objects.create(
                configuracao=config,
                numero_sequencial=config.sequencial_arquivo,
                tipo='CNAB240',
                nome_arquivo=nome_arquivo,
                conteudo=conteudo_cnab,
                quantidade_titulos=boletos.count(),
                valor_total=sum(b.valor_documento for b in boletos),
                status='GERADO'
            )
            
            # Associa boletos à remessa
            remessa.boletos.set(boletos)
            
            # Atualiza status dos boletos
            boletos.update(
                enviado_banco=True,
                data_envio_banco=timezone.now(),
                status='REGISTRADO'
            )
            
            # Incrementa sequencial
            config.sequencial_arquivo += 1
            config.save(update_fields=['sequencial_arquivo'])
            
            messages.success(request, f'Remessa {nome_arquivo} gerada com sucesso!')
            return redirect('boletos:detalhe_remessa', remessa_id=remessa.id)
            
        except Exception as e:
            import traceback
            erro_completo = traceback.format_exc()
            print(f"\n{'='*80}")
            print(f"ERRO AO GERAR REMESSA:")
            print(erro_completo)
            print(f"{'='*80}\n")
            messages.error(request, f'Erro ao gerar remessa: {str(e)}')
            return redirect('boletos:lista_boletos')
    
    # GET - Lista boletos disponíveis para remessa
    boletos = Boleto.objects.filter(
        status='EMITIDO',
        enviado_banco=False
    ).select_related('configuracao', 'cliente', 'parcela')
    
    configuracoes = ConfiguracaoBancaria.objects.filter(ativo=True)
    
    context = {
        'boletos': boletos,
        'configuracoes': configuracoes,
        'hoje': timezone.now().date().isoformat(),
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/gerar_remessa.html', context)


@login_required
@verificar_permissao_menu('/boletos/remessas/')
def detalhe_remessa(request, remessa_id):
    """Exibe detalhes de uma remessa"""
    remessa = get_object_or_404(RemessaCNAB, id=remessa_id)
    
    context = {
        'remessa': remessa,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/detalhe_remessa.html', context)


@login_required
@verificar_permissao_menu('/boletos/remessas/')
def download_remessa(request, remessa_id):
    """Faz download do arquivo de remessa"""
    remessa = get_object_or_404(RemessaCNAB, id=remessa_id)
    
    # Cria resposta com o arquivo
    response = HttpResponse(remessa.conteudo, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{remessa.nome_arquivo}"'
    
    # Atualiza status
    if remessa.status == 'GERADO':
        remessa.status = 'ENVIADO'
        remessa.data_envio = timezone.now()
        remessa.save()
    
    return response


@login_required
@verificar_permissao_menu('/boletos/remessas/')
def lista_remessas(request):
    """Lista todas as remessas"""
    remessas = RemessaCNAB.objects.select_related('configuracao').all().order_by('-data_geracao')
    
    context = {
        'remessas': remessas,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/lista_remessas.html', context)


@login_required
@verificar_permissao_acao('/boletos/boletos/', 'excluir')
def cancelar_boleto(request, boleto_id):
    """Cancela um boleto"""
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    if boleto.status in ['PAGO', 'CANCELADO']:
        messages.error(request, 'Boleto não pode ser cancelado.')
        return redirect('boletos:detalhe_boleto', boleto_id=boleto_id)
    
    if request.method == 'POST':
        boleto.status = 'CANCELADO'
        boleto.save()
        
        messages.success(request, 'Boleto cancelado com sucesso.')
        return redirect('boletos:lista_boletos')
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'boletos/cancelar_boleto.html', context)


# ============================================================================
# VIEWS DE CONFIGURAÇÃO BANCÁRIA
# ============================================================================

@login_required
@verificar_permissao_menu('/boletos/configuracoes/')
def lista_configuracoes(request):
    """Lista todas as configurações bancárias"""
    configuracoes = ConfiguracaoBancaria.objects.select_related('conta_financeira').all().order_by('-ativo', 'nome')
    
    context = {
        'configuracoes': configuracoes,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/lista_configuracoes.html', context)


@login_required
@verificar_permissao_acao('/boletos/configuracoes/', 'criar')
def criar_configuracao(request):
    """Cria uma nova configuração bancária"""
    if request.method == 'POST':
        form = ConfiguracaoBancariaForm(request.POST)
        if form.is_valid():
            configuracao = form.save()
            messages.success(request, f'Configuração "{configuracao.nome}" criada com sucesso!')
            return redirect('boletos:lista_configuracoes')
    else:
        form = ConfiguracaoBancariaForm()
    
    context = {
        'form': form,
        'titulo': 'Nova Configuração Bancária',
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/form_configuracao.html', context)


@login_required
@verificar_permissao_acao('/boletos/configuracoes/', 'editar')
def editar_configuracao(request, id):
    """Edita uma configuração bancária existente"""
    configuracao = get_object_or_404(ConfiguracaoBancaria, id=id)
    
    if request.method == 'POST':
        form = ConfiguracaoBancariaForm(request.POST, instance=configuracao)
        if form.is_valid():
            configuracao = form.save()
            messages.success(request, f'Configuração "{configuracao.nome}" atualizada com sucesso!')
            return redirect('boletos:lista_configuracoes')
    else:
        form = ConfiguracaoBancariaForm(instance=configuracao)
    
    context = {
        'form': form,
        'configuracao': configuracao,
        'titulo': f'Editar Configuração: {configuracao.nome}',
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/form_configuracao.html', context)


@login_required
@verificar_permissao_acao('/boletos/configuracoes/', 'excluir')
def excluir_configuracao(request, id):
    """Exclui uma configuração bancária"""
    configuracao = get_object_or_404(ConfiguracaoBancaria, id=id)
    
    if request.method == 'POST':
        nome = configuracao.nome
        configuracao.delete()
        messages.success(request, f'Configuração "{nome}" excluída com sucesso!')
        return redirect('boletos:lista_configuracoes')
    
    context = {
        'configuracao': configuracao,
        'hide_sidebar': True,
    }
    
    return render(request, 'boletos/confirmar_exclusao_configuracao.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Case, When, DecimalField
from django.http import JsonResponse
from datetime import date, timedelta
from decimal import Decimal

from usuarios.decorators import permissao_menu_required
from cadastros.models import ContaFinanceira
from .models import MovimentacaoFinanceira
from .forms_movimentacao import MovimentacaoFinanceiraForm, FiltroMovimentacaoForm


@login_required
@permissao_menu_required('financeiro', 'view')
def conta_corrente_list(request):
    """Lista todas as contas financeiras com saldos"""
    contas = ContaFinanceira.objects.filter(ativo=True).order_by('nome')
    
    contas_com_saldo = []
    for conta in contas:
        movimentacoes = MovimentacaoFinanceira.objects.filter(conta_financeira=conta)
        entradas = movimentacoes.filter(tipo='ENTRADA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        saidas = movimentacoes.filter(tipo='SAIDA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        saldo_atual = conta.saldo_inicial + entradas - saidas
        
        contas_com_saldo.append({
            'conta': conta,
            'saldo_inicial': conta.saldo_inicial,
            'entradas': entradas,
            'saidas': saidas,
            'saldo_atual': saldo_atual
        })
    
    context = {
        'contas': contas_com_saldo,
        'hide_sidebar': True,
    }
    return render(request, 'financeiro/conta_corrente_list.html', context)


@login_required
@permissao_menu_required('financeiro', 'view')
def extrato_conta(request, conta_id):
    """Exibe o extrato de uma conta financeira específica"""
    conta = get_object_or_404(ContaFinanceira, pk=conta_id)
    
    # Formulário de filtro
    filtro_form = FiltroMovimentacaoForm(request.GET or None)
    
    # Query base
    movimentacoes = MovimentacaoFinanceira.objects.filter(conta_financeira=conta)
    
    # Aplicar filtros
    if filtro_form.is_valid():
        if filtro_form.cleaned_data.get('tipo'):
            movimentacoes = movimentacoes.filter(tipo=filtro_form.cleaned_data['tipo'])
        
        if filtro_form.cleaned_data.get('origem'):
            movimentacoes = movimentacoes.filter(origem=filtro_form.cleaned_data['origem'])
        
        if filtro_form.cleaned_data.get('data_inicio'):
            movimentacoes = movimentacoes.filter(data__gte=filtro_form.cleaned_data['data_inicio'])
        
        if filtro_form.cleaned_data.get('data_fim'):
            movimentacoes = movimentacoes.filter(data__lte=filtro_form.cleaned_data['data_fim'])
    
    # Ordenar por data decrescente
    movimentacoes = movimentacoes.order_by('-data', '-criado_em').select_related('categoria', 'conta_destino')
    
    # Calcular totais
    entradas_total = movimentacoes.filter(tipo='ENTRADA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    saidas_total = movimentacoes.filter(tipo='SAIDA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    saldo_atual = conta.saldo_inicial + entradas_total - saidas_total
    
    context = {
        'conta': conta,
        'movimentacoes': movimentacoes,
        'filtro_form': filtro_form,
        'saldo_inicial': conta.saldo_inicial,
        'entradas_total': entradas_total,
        'saidas_total': saidas_total,
        'saldo_atual': saldo_atual,
        'hide_sidebar': True,
    }
    return render(request, 'financeiro/extrato_conta.html', context)


@login_required
@permissao_menu_required('financeiro', 'add')
def movimentacao_create(request):
    """Criar nova movimentação manual"""
    if request.method == 'POST':
        form = MovimentacaoFinanceiraForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.origem = 'MANUAL'
            movimentacao.usuario = request.user
            
            # Se for transferência, criar movimentação na conta destino
            if movimentacao.conta_destino:
                movimentacao.origem = 'TRANSFERENCIA'
                movimentacao.save()
                
                # Criar movimentação inversa na conta destino
                MovimentacaoFinanceira.objects.create(
                    conta_financeira=movimentacao.conta_destino,
                    data=movimentacao.data,
                    tipo='ENTRADA' if movimentacao.tipo == 'SAIDA' else 'SAIDA',
                    valor=movimentacao.valor,
                    descricao=f'Transferência de {movimentacao.conta_financeira.nome}',
                    origem='TRANSFERENCIA',
                    categoria=movimentacao.categoria,
                    observacoes=movimentacao.observacoes,
                    usuario=request.user
                )
            else:
                movimentacao.save()
            
            return redirect('financeiro:extrato_conta', conta_id=movimentacao.conta_financeira.pk)
    else:
        form = MovimentacaoFinanceiraForm()
        # Definir data padrão como hoje
        form.initial['data'] = date.today()
    
    context = {
        'form': form,
        'acao': 'criar',
        'hide_sidebar': True,
    }
    return render(request, 'financeiro/movimentacao_form.html', context)


@login_required
@permissao_menu_required('financeiro', 'change')
def movimentacao_edit(request, pk):
    """Editar movimentação existente (apenas manuais)"""
    movimentacao = get_object_or_404(MovimentacaoFinanceira, pk=pk)
    
    # Apenas movimentações manuais podem ser editadas
    if movimentacao.origem != 'MANUAL':
        return redirect('financeiro:extrato_conta', conta_id=movimentacao.conta_financeira.pk)
    
    if request.method == 'POST':
        form = MovimentacaoFinanceiraForm(request.POST, instance=movimentacao)
        if form.is_valid():
            form.save()
            return redirect('financeiro:extrato_conta', conta_id=movimentacao.conta_financeira.pk)
    else:
        form = MovimentacaoFinanceiraForm(instance=movimentacao)
    
    context = {
        'form': form,
        'movimentacao': movimentacao,
        'acao': 'editar',
        'hide_sidebar': True,
    }
    return render(request, 'financeiro/movimentacao_form.html', context)


@login_required
@permissao_menu_required('financeiro', 'delete')
def movimentacao_delete(request, pk):
    """Deletar movimentação (apenas manuais)"""
    movimentacao = get_object_or_404(MovimentacaoFinanceira, pk=pk)
    
    # Apenas movimentações manuais podem ser deletadas
    if movimentacao.origem == 'MANUAL' or movimentacao.origem == 'TRANSFERENCIA':
        conta_id = movimentacao.conta_financeira.pk
        movimentacao.delete()
        return redirect('financeiro:extrato_conta', conta_id=conta_id)
    
    return redirect('financeiro:extrato_conta', conta_id=movimentacao.conta_financeira.pk)

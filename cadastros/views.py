from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from usuarios.decorators import permissao_menu_required
from .models import PlanoConta, ContaFinanceira, MetodoPagamento, Fornecedor
from contas_receber.models import Cliente
from .forms import PlanoContaForm, ContaFinanceiraForm, MetodoPagamentoForm
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

@login_required
@permissao_menu_required('/cadastros/', 'visualizar')
def dashboard_cadastros(request):
    # Estatísticas de Clientes
    total_clientes = Cliente.objects.count()
    clientes_ativos = Cliente.objects.filter(ativo=True).count()
    clientes_inativos = total_clientes - clientes_ativos
    
    # Estatísticas de Fornecedores
    total_fornecedores = Fornecedor.objects.count()
    fornecedores_ativos = Fornecedor.objects.filter(ativo=True).count()
    fornecedores_inativos = total_fornecedores - fornecedores_ativos
    
    # Estatísticas de Contas Financeiras
    total_contas = ContaFinanceira.objects.count()
    contas_ativas = ContaFinanceira.objects.filter(ativo=True).count()
    contas_banco = ContaFinanceira.objects.filter(tipo='banco').count()
    contas_factory = ContaFinanceira.objects.filter(tipo='factory').count()
    saldo_total = ContaFinanceira.objects.filter(ativo=True).aggregate(total=Sum('saldo_inicial'))['total'] or 0
    
    # Estatísticas de Plano de Contas
    total_plano_contas = PlanoConta.objects.count()
    plano_contas_ativos = PlanoConta.objects.filter(ativo=True).count()
    plano_contas_pai = PlanoConta.objects.filter(pai__isnull=True).count()
    plano_contas_filhos = PlanoConta.objects.filter(pai__isnull=False).count()
    
    # Métodos de Pagamento
    total_metodos_pagamento = MetodoPagamento.objects.count()
    metodos_ativos = MetodoPagamento.objects.filter(ativo=True).count()
    
    # Últimos registros
    ultimos_clientes = Cliente.objects.order_by('-id')[:5]
    ultimos_fornecedores = Fornecedor.objects.order_by('-id')[:5]
    ultimas_contas = ContaFinanceira.objects.order_by('-criado_em')[:5]
    
    context = {
        'modulo_ativo': 'cadastros',
        'hide_sidebar': True,
        # Clientes
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'clientes_inativos': clientes_inativos,
        # Fornecedores
        'total_fornecedores': total_fornecedores,
        'fornecedores_ativos': fornecedores_ativos,
        'fornecedores_inativos': fornecedores_inativos,
        # Contas Financeiras
        'total_contas': total_contas,
        'contas_ativas': contas_ativas,
        'contas_banco': contas_banco,
        'contas_factory': contas_factory,
        'saldo_total': saldo_total,
        # Plano de Contas
        'total_plano_contas': total_plano_contas,
        'plano_contas_ativos': plano_contas_ativos,
        'plano_contas_pai': plano_contas_pai,
        'plano_contas_filhos': plano_contas_filhos,
        # Métodos de Pagamento
        'total_metodos_pagamento': total_metodos_pagamento,
        'metodos_ativos': metodos_ativos,
        # Últimos registros
        'ultimos_clientes': ultimos_clientes,
        'ultimos_fornecedores': ultimos_fornecedores,
        'ultimas_contas': ultimas_contas,
    }
    return render(request, 'cadastros/dashboard.html', context)

@login_required
@permissao_menu_required('/cadastros/plano-contas/', 'visualizar')
def plano_contas(request):
    registros = PlanoConta.objects.select_related('pai').order_by('codigo')
    form = PlanoContaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cadastros:plano_contas')
    context = {
        'modulo_ativo': 'cadastros',
        'registros': registros,
        'form': form,
        'hide_sidebar': True
    }
    return render(request, 'cadastros/plano_contas.html', context)

@login_required
@permissao_menu_required('/cadastros/plano-contas/', 'editar')
def editar_plano_conta(request, pk):
    conta = PlanoConta.objects.get(pk=pk)
    form = PlanoContaForm(request.POST or None, instance=conta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cadastros:plano_contas')
    registros = PlanoConta.objects.select_related('pai').order_by('codigo')
    context = {
        'modulo_ativo': 'cadastros',
        'registros': registros,
        'form': form,
        'editando': True,
        'conta': conta,
        'hide_sidebar': True
    }
    return render(request, 'cadastros/plano_contas.html', context)

@login_required
@permissao_menu_required('/cadastros/plano-contas/', 'excluir')
def inativar_plano_conta(request, pk):
    conta = PlanoConta.objects.get(pk=pk)
    conta.ativo = False
    conta.save()
    return redirect('cadastros:plano_contas')

@login_required
@permissao_menu_required('/cadastros/plano-contas/', 'editar')
def ativar_plano_conta(request, pk):
    conta = PlanoConta.objects.get(pk=pk)
    conta.ativo = True
    conta.save()
    return redirect('cadastros:plano_contas')

@login_required
@permissao_menu_required('/cadastros/contas-financeiras/', 'visualizar')
def contas_financeiras(request):
    contas = ContaFinanceira.objects.order_by('nome')
    form = ContaFinanceiraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cadastros:contas_financeiras')
    context = {
        'modulo_ativo': 'cadastros',
        'contas': contas,
        'form': form,
        'hide_sidebar': True
    }
    return render(request, 'cadastros/contas_financeiras.html', context)

@login_required
@permissao_menu_required('/cadastros/contas-financeiras/', 'editar')
def editar_conta_financeira(request, pk):
    conta = get_object_or_404(ContaFinanceira, pk=pk)
    
    if request.method == 'POST':
        form = ContaFinanceiraForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta financeira editada com sucesso!')
            return redirect('cadastros:contas_financeiras')
    else:
        form = ContaFinanceiraForm(instance=conta)
    
    contas = ContaFinanceira.objects.all().order_by('nome')
    return render(request, 'cadastros/contas_financeiras.html', {
        'form': form,
        'contas': contas,
        'editando': True,
        'hide_sidebar': True
    })

@login_required
@permissao_menu_required('/cadastros/contas-financeiras/', 'editar')
def inativar_conta_financeira(request, pk):
    conta = get_object_or_404(ContaFinanceira, pk=pk)
    conta.ativo = False
    conta.save()
    messages.success(request, f'Conta "{conta.nome}" inativada com sucesso!')
    return redirect('cadastros:contas_financeiras')

@login_required
@permissao_menu_required('/cadastros/contas-financeiras/', 'editar')
def ativar_conta_financeira(request, pk):
    conta = get_object_or_404(ContaFinanceira, pk=pk)
    conta.ativo = True
    conta.save()
    messages.success(request, f'Conta "{conta.nome}" ativada com sucesso!')
    return redirect('cadastros:contas_financeiras')

@login_required
@permissao_menu_required('/cadastros/metodos-pagamento/', 'visualizar')
def metodos_pagamento(request):
    metodos = MetodoPagamento.objects.order_by('nome')
    form = MetodoPagamentoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        metodo = form.save(commit=False)
        metodo.usuario = request.user
        metodo.save()
        messages.success(request, f'Método de pagamento "{metodo.nome}" criado com sucesso!')
        return redirect('cadastros:metodos_pagamento')
    context = {
        'modulo_ativo': 'cadastros',
        'metodos': metodos,
        'form': form,
        'hide_sidebar': True
    }
    return render(request, 'cadastros/metodos_pagamento.html', context)

@login_required
@permissao_menu_required('/cadastros/metodos-pagamento/', 'editar')
def editar_metodo_pagamento(request, pk):
    metodo = get_object_or_404(MetodoPagamento, pk=pk)
    
    if request.method == 'POST':
        form = MetodoPagamentoForm(request.POST, instance=metodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pagamento editado com sucesso!')
            return redirect('cadastros:metodos_pagamento')
    else:
        form = MetodoPagamentoForm(instance=metodo)
    
    metodos = MetodoPagamento.objects.all().order_by('nome')
    return render(request, 'cadastros/metodos_pagamento.html', {
        'form': form,
        'metodos': metodos,
        'editando': True,
        'hide_sidebar': True
    })

@login_required
@permissao_menu_required('/cadastros/metodos-pagamento/', 'editar')
def inativar_metodo_pagamento(request, pk):
    metodo = get_object_or_404(MetodoPagamento, pk=pk)
    metodo.ativo = False
    metodo.save()
    messages.success(request, f'Método de pagamento "{metodo.nome}" inativado com sucesso!')
    return redirect('cadastros:metodos_pagamento')

@login_required
@permissao_menu_required('/cadastros/metodos-pagamento/', 'editar')
def ativar_metodo_pagamento(request, pk):
    metodo = get_object_or_404(MetodoPagamento, pk=pk)
    metodo.ativo = True
    metodo.save()
    messages.success(request, f'Método de pagamento "{metodo.nome}" ativado com sucesso!')
    return redirect('cadastros:metodos_pagamento')

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorios_cadastros(request):
    contas = ContaFinanceira.objects.order_by('nome')
    form = ContaFinanceiraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cadastros:contas_financeiras')
    context = {
        'modulo_ativo': 'cadastros',
        'contas': contas,
        'form': form,
        'hide_sidebar': True
    }
    return render(request, 'cadastros/contas_financeiras.html', context)

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorios_cadastros(request):
    context = {
        'modulo_ativo': 'cadastros',
        'hide_sidebar': True
    }
    return render(request, 'cadastros/relatorios.html', context)

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_plano_contas_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="plano_contas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Plano de Contas", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca todas as contas ordenadas por código
    contas = PlanoConta.objects.select_related('pai').order_by('codigo')
    
    # Função recursiva para construir hierarquia
    def construir_hierarquia(pai_id=None, nivel=0):
        linhas = []
        contas_filtradas = [c for c in contas if (c.pai_id == pai_id)]
        
        for conta in contas_filtradas:
            # Indentação baseada no nível
            indent = '    ' * nivel
            nome_indentado = f"{indent}{conta.nome}"
            status = 'Ativo' if conta.ativo else 'Inativo'
            
            # Adiciona a linha da conta
            linhas.append([
                str(conta.id),
                conta.codigo,
                nome_indentado,
                status
            ])
            
            # Adiciona filhos recursivamente
            filhos = construir_hierarquia(conta.id, nivel + 1)
            linhas.extend(filhos)
        
        return linhas
    
    # Cabeçalho da tabela
    data = [['ID', 'Código', 'Nome da Conta', 'Status']]
    
    # Adiciona as contas hierarquicamente (começando pelas raiz)
    data.extend(construir_hierarquia(None, 0))
    
    # Cria a tabela
    table = Table(data, colWidths=[2*cm, 3*cm, 10*cm, 2.5*cm])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centralizado
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Código à esquerda
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Nome à esquerda
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Status centralizado
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Rodapé
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Total de contas: {len(contas)}", footer_style))
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_contas_ativas_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contas_ativas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Contas Ativas", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca apenas contas ativas ordenadas por código
    contas = PlanoConta.objects.filter(ativo=True).select_related('pai').order_by('codigo')
    
    # Função recursiva para construir hierarquia
    def construir_hierarquia(pai_id=None, nivel=0):
        linhas = []
        contas_filtradas = [c for c in contas if (c.pai_id == pai_id)]
        
        for conta in contas_filtradas:
            # Indentação baseada no nível
            indent = '    ' * nivel
            nome_indentado = f"{indent}{conta.nome}"
            conta_pai = conta.pai.nome if conta.pai else '-'
            
            # Adiciona a linha da conta
            linhas.append([
                str(conta.id),
                conta.codigo,
                nome_indentado,
                conta_pai
            ])
            
            # Adiciona filhos recursivamente
            filhos = construir_hierarquia(conta.id, nivel + 1)
            linhas.extend(filhos)
        
        return linhas
    
    # Cabeçalho da tabela
    data = [['ID', 'Código', 'Nome da Conta', 'Conta Pai']]
    
    # Adiciona as contas hierarquicamente (começando pelas raiz)
    data.extend(construir_hierarquia(None, 0))
    
    # Cria a tabela
    table = Table(data, colWidths=[2*cm, 3*cm, 8*cm, 4.5*cm])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Rodapé
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Total de contas ativas: {len(contas)}", footer_style))
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_contas_inativas_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contas_inativas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Contas Inativas", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca apenas contas inativas ordenadas por código
    contas = PlanoConta.objects.filter(ativo=False).select_related('pai').order_by('codigo')
    
    # Função recursiva para construir hierarquia
    def construir_hierarquia(pai_id=None, nivel=0):
        linhas = []
        contas_filtradas = [c for c in contas if (c.pai_id == pai_id)]
        
        for conta in contas_filtradas:
            # Indentação baseada no nível
            indent = '    ' * nivel
            nome_indentado = f"{indent}{conta.nome}"
            conta_pai = conta.pai.nome if conta.pai else '-'
            
            # Adiciona a linha da conta
            linhas.append([
                str(conta.id),
                conta.codigo,
                nome_indentado,
                conta_pai
            ])
            
            # Adiciona filhos recursivamente
            filhos = construir_hierarquia(conta.id, nivel + 1)
            linhas.extend(filhos)
        
        return linhas
    
    # Cabeçalho da tabela
    data = [['ID', 'Código', 'Nome da Conta', 'Conta Pai']]
    
    # Adiciona as contas hierarquicamente (começando pelas raiz)
    data.extend(construir_hierarquia(None, 0))
    
    # Cria a tabela
    table = Table(data, colWidths=[2*cm, 3*cm, 8*cm, 4.5*cm])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Rodapé
    elements.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Total de contas inativas: {len(contas)}", footer_style))
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_hierarquia_completa_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="hierarquia_completa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Hierarquia Completa do Plano de Contas", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca todas as contas ordenadas por código
    contas = PlanoConta.objects.select_related('pai').order_by('codigo')
    
    # Função recursiva para construir hierarquia com níveis visuais
    def construir_hierarquia(pai_id=None, nivel=0):
        linhas = []
        contas_filtradas = [c for c in contas if (c.pai_id == pai_id)]
        
        for conta in contas_filtradas:
            # Símbolos de hierarquia baseados no nível
            if nivel == 0:
                prefixo = '▪'
            elif nivel == 1:
                prefixo = '  ├─'
            elif nivel == 2:
                prefixo = '    ├──'
            else:
                prefixo = '      ' + ('─' * nivel) + '►'
            
            nome_hierarquico = f"{prefixo} {conta.nome}"
            status = '✓' if conta.ativo else '✗'
            conta_pai = conta.pai.nome if conta.pai else 'RAIZ'
            
            # Adiciona a linha da conta
            linhas.append([
                str(conta.id),
                conta.codigo,
                nome_hierarquico,
                conta_pai,
                status
            ])
            
            # Adiciona filhos recursivamente
            filhos = construir_hierarquia(conta.id, nivel + 1)
            linhas.extend(filhos)
        
        return linhas
    
    # Cabeçalho da tabela
    data = [['ID', 'Código', 'Estrutura Hierárquica', 'Pai', 'Ativo']]
    
    # Adiciona as contas hierarquicamente (começando pelas raiz)
    data.extend(construir_hierarquia(None, 0))
    
    # Cria a tabela
    table = Table(data, colWidths=[1.5*cm, 2.5*cm, 8.5*cm, 3.5*cm, 1.5*cm])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Estatísticas no rodapé
    elements.append(Spacer(1, 0.8*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    
    total_contas = len(contas)
    contas_ativas = contas.filter(ativo=True).count()
    contas_inativas = contas.filter(ativo=False).count()
    contas_raiz = contas.filter(pai__isnull=True).count()
    
    elements.append(Paragraph(
        f"Total: {total_contas} contas | Ativas: {contas_ativas} | Inativas: {contas_inativas} | Contas Raiz: {contas_raiz}",
        footer_style
    ))
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_contas_bancarias_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contas_bancarias_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Contas Bancárias e Factory", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca todas as contas ordenadas por nome
    contas = ContaFinanceira.objects.order_by('tipo', 'nome')
    
    # Cabeçalho da tabela
    data = [['Nome', 'Tipo', 'Agência', 'Conta', 'Status']]
    
    # Adiciona as contas
    for conta in contas:
        status = 'Ativo' if conta.ativo else 'Inativo'
        tipo = conta.get_tipo_display()
        agencia = conta.agencia if conta.agencia else '-'
        conta_num = conta.conta if conta.conta else '-'
        
        data.append([
            conta.nome,
            tipo,
            agencia,
            conta_num,
            status
        ])
    
    # Cria a tabela
    table = Table(data, colWidths=[5*cm, 3*cm, 2.5*cm, 3*cm, 2*cm])
    
    # Estilo da tabela
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Estatísticas no rodapé
    elements.append(Spacer(1, 0.8*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    
    total_contas = len(contas)
    contas_ativas = contas.filter(ativo=True).count()
    contas_inativas = contas.filter(ativo=False).count()
    contas_banco = contas.filter(tipo='banco').count()
    contas_factory = contas.filter(tipo='factory').count()
    
    elements.append(Paragraph(
        f"Total: {total_contas} | Ativas: {contas_ativas} | Inativas: {contas_inativas} | Bancos: {contas_banco} | Factory: {contas_factory}",
        footer_style
    ))
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_consolidado_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_consolidado_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Título
    elements.append(Paragraph("Relatório Consolidado - Cadastros", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca dados
    plano_contas = PlanoConta.objects.all()
    contas_financeiras = ContaFinanceira.objects.all()
    
    # ===== RESUMO PLANO DE CONTAS =====
    elements.append(Paragraph("Plano de Contas", section_title_style))
    
    data_plano = [['Categoria', 'Quantidade']]
    data_plano.append(['Total de Contas', str(plano_contas.count())])
    data_plano.append(['Contas Ativas', str(plano_contas.filter(ativo=True).count())])
    data_plano.append(['Contas Inativas', str(plano_contas.filter(ativo=False).count())])
    data_plano.append(['Contas Raiz', str(plano_contas.filter(pai__isnull=True).count())])
    data_plano.append(['Contas Filhas', str(plano_contas.filter(pai__isnull=False).count())])
    
    table_plano = Table(data_plano, colWidths=[10*cm, 5*cm])
    table_plano.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table_plano)
    elements.append(Spacer(1, 0.8*cm))
    
    # ===== RESUMO CONTAS FINANCEIRAS =====
    elements.append(Paragraph("Contas Bancárias e Factory", section_title_style))
    
    data_financeiras = [['Categoria', 'Quantidade']]
    data_financeiras.append(['Total de Contas', str(contas_financeiras.count())])
    data_financeiras.append(['Contas Ativas', str(contas_financeiras.filter(ativo=True).count())])
    data_financeiras.append(['Contas Inativas', str(contas_financeiras.filter(ativo=False).count())])
    data_financeiras.append(['Bancos', str(contas_financeiras.filter(tipo='banco').count())])
    data_financeiras.append(['Factory', str(contas_financeiras.filter(tipo='factory').count())])
    
    table_financeiras = Table(data_financeiras, colWidths=[10*cm, 5*cm])
    table_financeiras.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table_financeiras)
    
    # Gera o PDF
    doc.build(elements)
    return response

@login_required
@permissao_menu_required('/cadastros/relatorios/', 'visualizar')
def relatorio_metodos_pagamento_pdf(request):
    # Cria a resposta HTTP com tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="metodos_pagamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("Métodos de Pagamento", title_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Busca todos os métodos ordenados por nome
    metodos = MetodoPagamento.objects.select_related('usuario').order_by('nome')
    
    # Monta dados da tabela
    data = [['ID', 'Nome', 'Ativo', 'Criado em', 'Usuário']]
    
    for metodo in metodos:
        status = 'Ativo' if metodo.ativo else 'Inativo'
        usuario = metodo.usuario.username if metodo.usuario else '-'
        criado = metodo.criado_em.strftime('%d/%m/%Y')
        data.append([
            str(metodo.id),
            metodo.nome,
            status,
            criado,
            usuario
        ])
    
    # Cria tabela
    table = Table(data, colWidths=[2*cm, 6*cm, 2.5*cm, 3*cm, 3.5*cm])
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centralizado
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Nome à esquerda
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Ativo centralizado
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Data centralizada
        ('ALIGN', (4, 1), (4, -1), 'LEFT'),    # Usuário à esquerda
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    
    elements.append(table)
    
    # Rodapé com estatísticas
    elements.append(Spacer(1, 1*cm))
    total_metodos = metodos.count()
    metodos_ativos = metodos.filter(ativo=True).count()
    metodos_inativos = metodos.filter(ativo=False).count()
    
    elements.append(Paragraph(
        f"Total: {total_metodos} | Ativos: {metodos_ativos} | Inativos: {metodos_inativos}",
        footer_style
    ))
    
    # Gera o PDF
    doc.build(elements)
    return response

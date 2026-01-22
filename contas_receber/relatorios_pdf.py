"""
Módulo de geração de relatórios em PDF para Contas a Receber
Utiliza ReportLab para criar relatórios profissionais
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from io import BytesIO

from django.db.models import Sum, Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfgen import canvas

from .models import Parcela, Cliente


class RelatorioBase:
    """Classe base para todos os relatórios"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.titulo_style = ParagraphStyle(
            'TituloCustom',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        self.subtitulo_style = ParagraphStyle(
            'SubtituloCustom',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER
        )
    
    def criar_cabecalho(self, titulo, subtitulo=None):
        """Cria cabeçalho padrão do relatório"""
        elementos = []
        elementos.append(Paragraph(titulo, self.titulo_style))
        if subtitulo:
            elementos.append(Paragraph(subtitulo, self.subtitulo_style))
        elementos.append(Spacer(1, 10*mm))
        return elementos
    
    def formatar_moeda(self, valor):
        """Formata valor como moeda brasileira"""
        if valor is None:
            return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    def formatar_data(self, data):
        """Formata data no padrão brasileiro"""
        if isinstance(data, str):
            return data
        return data.strftime('%d/%m/%Y') if data else '-'


class RelatorioTitulosVencer(RelatorioBase):
    """Relatório de Títulos a Vencer (próximos 30 dias)"""
    
    def gerar(self, dias=30, cliente_id=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        
        # Cabeçalho
        data_limite = date.today() + timedelta(days=dias)
        subtitulo = f"Vencimentos de {date.today().strftime('%d/%m/%Y')} até {data_limite.strftime('%d/%m/%Y')}"
        elementos.extend(self.criar_cabecalho("RELATÓRIO DE TÍTULOS A VENCER", subtitulo))
        
        # Filtrar parcelas
        parcelas = Parcela.objects.filter(
            status_pagamento='pendente',
            data_vencimento__gte=date.today(),
            data_vencimento__lte=data_limite
        ).select_related('cliente', 'nota_fiscal').order_by('data_vencimento')
        
        if cliente_id:
            parcelas = parcelas.filter(cliente_id=cliente_id)
        
        # Dados da tabela
        dados = [['Vencimento', 'Cliente', 'NF', 'Parcela', 'Valor', 'Dias p/ Vencer']]
        
        total = Decimal('0')
        for parcela in parcelas:
            dias_vencer = (parcela.data_vencimento - date.today()).days
            dados.append([
                self.formatar_data(parcela.data_vencimento),
                parcela.cliente.nome[:30],
                parcela.nota_fiscal.numero_nota,
                f"{parcela.numero_parcela}",
                self.formatar_moeda(parcela.valor),
                str(dias_vencer)
            ])
            total += parcela.valor
        
        # Linha de total
        dados.append(['', '', '', 'TOTAL:', self.formatar_moeda(total), ''])
        
        # Criar tabela
        tabela = Table(dados, colWidths=[25*mm, 70*mm, 25*mm, 20*mm, 30*mm, 25*mm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10*mm))
        
        # Resumo
        resumo_texto = f"Total de parcelas: {len(parcelas)} | Valor total: {self.formatar_moeda(total)}"
        elementos.append(Paragraph(resumo_texto, self.subtitulo_style))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class RelatorioTitulosVencidos(RelatorioBase):
    """Relatório de Títulos Vencidos (Inadimplência)"""
    
    def gerar(self, cliente_id=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        
        # Cabeçalho
        subtitulo = f"Posição em {date.today().strftime('%d/%m/%Y')}"
        elementos.extend(self.criar_cabecalho("RELATÓRIO DE INADIMPLÊNCIA", subtitulo))
        
        # Filtrar parcelas vencidas
        parcelas = Parcela.objects.filter(
            status_pagamento='pendente',
            data_vencimento__lt=date.today()
        ).select_related('cliente', 'nota_fiscal').order_by('data_vencimento')
        
        if cliente_id:
            parcelas = parcelas.filter(cliente_id=cliente_id)
        
        # Dados da tabela
        dados = [['Vencimento', 'Cliente', 'NF', 'Parcela', 'Valor', 'Dias Atraso']]
        
        total = Decimal('0')
        for parcela in parcelas:
            dias_atraso = (date.today() - parcela.data_vencimento).days
            dados.append([
                self.formatar_data(parcela.data_vencimento),
                parcela.cliente.nome[:30],
                parcela.nota_fiscal.numero_nota,
                f"{parcela.numero_parcela}",
                self.formatar_moeda(parcela.valor),
                str(dias_atraso)
            ])
            total += parcela.valor
        
        # Linha de total
        dados.append(['', '', '', 'TOTAL:', self.formatar_moeda(total), ''])
        
        # Criar tabela com destaque vermelho
        tabela = Table(dados, colWidths=[25*mm, 70*mm, 25*mm, 20*mm, 30*mm, 25*mm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#fee2e2')),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fca5a5')),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10*mm))
        
        # Resumo
        resumo_texto = f"Total de parcelas vencidas: {len(parcelas)} | Valor total em atraso: {self.formatar_moeda(total)}"
        elementos.append(Paragraph(resumo_texto, self.subtitulo_style))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class RelatorioRecebimentos(RelatorioBase):
    """Relatório de Recebimentos Realizados"""
    
    def gerar(self, data_inicio, data_fim, cliente_id=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        
        # Cabeçalho
        subtitulo = f"Período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elementos.extend(self.criar_cabecalho("RELATÓRIO DE RECEBIMENTOS", subtitulo))
        
        # Filtrar parcelas pagas
        parcelas = Parcela.objects.filter(
            status_pagamento='pago',
            data_pagamento__gte=data_inicio,
            data_pagamento__lte=data_fim
        ).select_related('cliente', 'nota_fiscal').order_by('data_pagamento')
        
        if cliente_id:
            parcelas = parcelas.filter(cliente_id=cliente_id)
        
        # Dados da tabela
        dados = [['Data Pgto', 'Cliente', 'NF', 'Parcela', 'Vencimento', 'Valor Pago']]
        
        total = Decimal('0')
        for parcela in parcelas:
            dados.append([
                self.formatar_data(parcela.data_pagamento),
                parcela.cliente.nome[:30],
                parcela.nota_fiscal.numero_nota,
                f"{parcela.numero_parcela}",
                self.formatar_data(parcela.data_vencimento),
                self.formatar_moeda(parcela.valor_pago)
            ])
            total += parcela.valor_pago
        
        # Linha de total
        dados.append(['', '', '', '', 'TOTAL:', self.formatar_moeda(total)])
        
        # Criar tabela
        tabela = Table(dados, colWidths=[25*mm, 70*mm, 25*mm, 20*mm, 25*mm, 30*mm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#d1fae5')),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#a7f3d0')),
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 10*mm))
        
        # Resumo
        resumo_texto = f"Total de recebimentos: {len(parcelas)} | Valor total recebido: {self.formatar_moeda(total)}"
        elementos.append(Paragraph(resumo_texto, self.subtitulo_style))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class RelatorioExtratoPeriodo(RelatorioBase):
    """Relatório de Extrato Completo por Período"""
    
    def gerar(self, data_inicio, data_fim):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=1.5*cm, bottomMargin=1.5*cm)
        elementos = []
        
        # Cabeçalho
        subtitulo = f"Período: {self.formatar_data(data_inicio)} a {self.formatar_data(data_fim)}"
        elementos.extend(self.criar_cabecalho("EXTRATO POR PERÍODO", subtitulo))
        
        # Buscar parcelas do período
        parcelas_pagas = Parcela.objects.filter(
            status_pagamento='pago',
            data_pagamento__gte=data_inicio,
            data_pagamento__lte=data_fim
        ).select_related('nota_fiscal', 'nota_fiscal__cliente').order_by('data_pagamento')
        
        parcelas_vencidas = Parcela.objects.filter(
            status_pagamento='pendente',
            data_vencimento__lt=date.today(),
            data_vencimento__gte=data_inicio,
            data_vencimento__lte=data_fim
        ).select_related('nota_fiscal', 'nota_fiscal__cliente').order_by('data_vencimento')
        
        hoje = date.today()
        data_inicio_vencer = max(hoje, data_inicio)
        parcelas_a_vencer = Parcela.objects.filter(
            status_pagamento='pendente',
            data_vencimento__gte=data_inicio_vencer,
            data_vencimento__lte=data_fim
        ).select_related('nota_fiscal', 'nota_fiscal__cliente').order_by('data_vencimento')
        
        # ===== PARCELAS PAGAS =====
        if parcelas_pagas.exists():
            elementos.append(Spacer(1, 5*mm))
            titulo_pago = Paragraph("<b>PARCELAS PAGAS</b>", 
                ParagraphStyle('TituloPago', parent=self.styles['Normal'], fontSize=11, 
                              textColor=colors.HexColor('#059669'), alignment=TA_LEFT))
            elementos.append(titulo_pago)
            elementos.append(Spacer(1, 3*mm))
            
            dados_pago = [['Vencimento', 'Pagamento', 'Cliente', 'NF', 'Parc', 'Valor']]
            total_pago = Decimal('0')
            
            for parcela in parcelas_pagas:
                dados_pago.append([
                    self.formatar_data(parcela.data_vencimento),
                    self.formatar_data(parcela.data_pagamento),
                    parcela.nota_fiscal.cliente.nome[:30] if parcela.nota_fiscal and parcela.nota_fiscal.cliente else '-',
                    parcela.nota_fiscal.numero_nota if parcela.nota_fiscal else '-',
                    str(parcela.numero_parcela),
                    self.formatar_moeda(parcela.valor)
                ])
                total_pago += parcela.valor
            
            dados_pago.append(['', '', '', '', 'TOTAL PAGO:', self.formatar_moeda(total_pago)])
            
            tabela_pago = Table(dados_pago, colWidths=[28*mm, 28*mm, 95*mm, 30*mm, 18*mm, 30*mm])
            tabela_pago.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D1FAE5')),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ]))
            elementos.append(tabela_pago)
        
        # ===== PARCELAS VENCIDAS =====
        if parcelas_vencidas.exists():
            elementos.append(Spacer(1, 8*mm))
            titulo_vencido = Paragraph("<b>PARCELAS VENCIDAS (INADIMPLÊNCIA)</b>", 
                ParagraphStyle('TituloVencido', parent=self.styles['Normal'], fontSize=11, 
                              textColor=colors.HexColor('#DC2626'), alignment=TA_LEFT))
            elementos.append(titulo_vencido)
            elementos.append(Spacer(1, 3*mm))
            
            dados_vencido = [['Vencimento', 'Dias Atraso', 'Cliente', 'NF', 'Parc', 'Valor']]
            total_vencido = Decimal('0')
            
            for parcela in parcelas_vencidas:
                dias_atraso = (date.today() - parcela.data_vencimento).days
                dados_vencido.append([
                    self.formatar_data(parcela.data_vencimento),
                    str(dias_atraso),
                    parcela.nota_fiscal.cliente.nome[:30] if parcela.nota_fiscal and parcela.nota_fiscal.cliente else '-',
                    parcela.nota_fiscal.numero_nota if parcela.nota_fiscal else '-',
                    str(parcela.numero_parcela),
                    self.formatar_moeda(parcela.valor)
                ])
                total_vencido += parcela.valor
            
            dados_vencido.append(['', '', '', '', 'TOTAL VENCIDO:', self.formatar_moeda(total_vencido)])
            
            tabela_vencido = Table(dados_vencido, colWidths=[28*mm, 28*mm, 95*mm, 30*mm, 18*mm, 30*mm])
            tabela_vencido.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#FEE2E2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FCA5A5')),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ]))
            elementos.append(tabela_vencido)
        
        # ===== PARCELAS A VENCER =====
        if parcelas_a_vencer.exists():
            elementos.append(Spacer(1, 8*mm))
            titulo_vencer = Paragraph("<b>PARCELAS A VENCER</b>", 
                ParagraphStyle('TituloVencer', parent=self.styles['Normal'], fontSize=11, 
                              textColor=colors.HexColor('#F59E0B'), alignment=TA_LEFT))
            elementos.append(titulo_vencer)
            elementos.append(Spacer(1, 3*mm))
            
            dados_vencer = [['Vencimento', 'Dias p/ Vencer', 'Cliente', 'NF', 'Parc', 'Valor']]
            total_a_vencer = Decimal('0')
            
            for parcela in parcelas_a_vencer:
                dias_vencer = (parcela.data_vencimento - date.today()).days
                dados_vencer.append([
                    self.formatar_data(parcela.data_vencimento),
                    str(dias_vencer),
                    parcela.nota_fiscal.cliente.nome[:30] if parcela.nota_fiscal and parcela.nota_fiscal.cliente else '-',
                    parcela.nota_fiscal.numero_nota if parcela.nota_fiscal else '-',
                    str(parcela.numero_parcela),
                    self.formatar_moeda(parcela.valor)
                ])
                total_a_vencer += parcela.valor
            
            dados_vencer.append(['', '', '', '', 'TOTAL A VENCER:', self.formatar_moeda(total_a_vencer)])
            
            tabela_vencer = Table(dados_vencer, colWidths=[28*mm, 28*mm, 95*mm, 30*mm, 18*mm, 30*mm])
            tabela_vencer.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEF3C7')),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ]))
            elementos.append(tabela_vencer)
        
        # ===== RESUMO =====
        elementos.append(Spacer(1, 10*mm))
        total_geral_pago = sum(p.valor for p in parcelas_pagas)
        total_geral_vencido = sum(p.valor for p in parcelas_vencidas)
        total_geral_a_vencer = sum(p.valor for p in parcelas_a_vencer)
        
        resumo_texto = f"""
        <b>RESUMO DO PERÍODO:</b><br/>
        Pagas: {parcelas_pagas.count()} parcelas | {self.formatar_moeda(total_geral_pago)}<br/>
        Vencidas: {parcelas_vencidas.count()} parcelas | {self.formatar_moeda(total_geral_vencido)}<br/>
        A Vencer: {parcelas_a_vencer.count()} parcelas | {self.formatar_moeda(total_geral_a_vencer)}
        """
        elementos.append(Paragraph(resumo_texto, self.subtitulo_style))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class RelatorioFluxoCaixa(RelatorioBase):
    """Relatório de Fluxo de Caixa Projetado"""
    
    def gerar(self, dias=60):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        
        # Cabeçalho
        data_fim = date.today() + timedelta(days=dias)
        subtitulo = f"Projeção de {date.today().strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elementos.extend(self.criar_cabecalho("FLUXO DE CAIXA PROJETADO", subtitulo))
        
        # Agrupar por semana
        dados = [['Período', 'Qtd Parcelas', 'Valor Previsto']]
        
        data_atual = date.today()
        total_geral = Decimal('0')
        
        while data_atual <= data_fim:
            data_fim_semana = data_atual + timedelta(days=6)
            
            parcelas = Parcela.objects.filter(
                status_pagamento='pendente',
                data_vencimento__gte=data_atual,
                data_vencimento__lte=data_fim_semana
            )
            
            qtd = parcelas.count()
            total = parcelas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
            
            periodo = f"{data_atual.strftime('%d/%m')} a {data_fim_semana.strftime('%d/%m/%Y')}"
            dados.append([periodo, str(qtd), self.formatar_moeda(total)])
            
            total_geral += total
            data_atual = data_fim_semana + timedelta(days=1)
        
        # Linha de total
        dados.append(['TOTAL GERAL:', '', self.formatar_moeda(total_geral)])
        
        # Criar tabela
        tabela = Table(dados, colWidths=[80*mm, 40*mm, 50*mm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        
        elementos.append(tabela)
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class RelatorioPorCliente(RelatorioBase):
    """Relatório Completo por Cliente"""
    
    def gerar(self, cliente_id):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elementos = []
        
        cliente = Cliente.objects.get(id=cliente_id)
        
        # Cabeçalho
        elementos.extend(self.criar_cabecalho(
            "RELATÓRIO DE CLIENTE",
            f"{cliente.nome} - {cliente.cpf_cnpj}"
        ))
        
        # Estatísticas
        parcelas_pendentes = Parcela.objects.filter(cliente=cliente, status_pagamento='pendente')
        total_pendente = parcelas_pendentes.aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        parcelas_pagas = Parcela.objects.filter(cliente=cliente, status_pagamento='pago')
        total_pago = parcelas_pagas.aggregate(total=Sum('valor_pago'))['total'] or Decimal('0')
        
        parcelas_vencidas = parcelas_pendentes.filter(data_vencimento__lt=date.today())
        total_vencido = parcelas_vencidas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        # Tabela de resumo
        resumo_dados = [
            ['Indicador', 'Quantidade', 'Valor'],
            ['Parcelas Pendentes', str(parcelas_pendentes.count()), self.formatar_moeda(total_pendente)],
            ['Parcelas Vencidas', str(parcelas_vencidas.count()), self.formatar_moeda(total_vencido)],
            ['Parcelas Pagas', str(parcelas_pagas.count()), self.formatar_moeda(total_pago)],
        ]
        
        tabela_resumo = Table(resumo_dados, colWidths=[80*mm, 40*mm, 50*mm])
        tabela_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ]))
        
        elementos.append(tabela_resumo)
        elementos.append(Spacer(1, 10*mm))
        
        # Parcelas pendentes detalhadas
        if parcelas_pendentes.exists():
            elementos.append(Paragraph("Parcelas Pendentes", self.subtitulo_style))
            
            dados = [['Vencimento', 'NF', 'Parcela', 'Valor', 'Status']]
            for parcela in parcelas_pendentes.order_by('data_vencimento'):
                if parcela.data_vencimento < date.today():
                    status = f"VENCIDO há {(date.today() - parcela.data_vencimento).days} dias"
                else:
                    status = f"Vence em {(parcela.data_vencimento - date.today()).days} dias"
                
                dados.append([
                    self.formatar_data(parcela.data_vencimento),
                    parcela.nota_fiscal.numero_nota,
                    str(parcela.numero_parcela),
                    self.formatar_moeda(parcela.valor),
                    status
                ])
            
            tabela_pendentes = Table(dados, colWidths=[30*mm, 30*mm, 25*mm, 35*mm, 50*mm])
            tabela_pendentes.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ]))
            
            elementos.append(tabela_pendentes)
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer

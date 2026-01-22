from django.db import models
from django.contrib.auth.models import User
from cadastros.models import PlanoConta, ContaFinanceira, MetodoPagamento, Fornecedor


class ContaPagar(models.Model):
    """Registro de contas a pagar"""
    
    CLASSIFICACAO_CHOICES = [
        ('CUSTO', 'Custo'),
        ('DESPESA', 'Despesa'),
    ]
    
    conta = models.ForeignKey(PlanoConta, on_delete=models.PROTECT, related_name='contas_pagar_principais', verbose_name='Conta Principal')
    subconta = models.ForeignKey(PlanoConta, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagar_subcontas', verbose_name='Subconta')
    
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='contas_pagar', verbose_name='Fornecedor')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    vencimento = models.DateField(verbose_name='Data de Vencimento')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    
    data_pagamento = models.DateField(null=True, blank=True, verbose_name='Data de Pagamento')
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor Pago')
    juros = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Juros')
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Desconto')
    
    pago_atrasado = models.BooleanField(default=False, verbose_name='Pago Atrasado')
    pago = models.BooleanField(default=False, verbose_name='Pago')
    
    conta_financeira = models.ForeignKey(ContaFinanceira, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Conta Financeira')
    metodo_pagamento = models.ForeignKey(MetodoPagamento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Método de Pagamento')
    classificacao = models.CharField(max_length=10, choices=CLASSIFICACAO_CHOICES, default='DESPESA', verbose_name='Classificação')
    
    numero_documento = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número do Documento')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagar')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['-vencimento']
        indexes = [
            models.Index(fields=['vencimento']),
            models.Index(fields=['pago']),
        ]
    
    def __str__(self):
        status = "✓ Pago" if self.pago else "⟳ Pendente"
        return f"{self.fornecedor.nome} - R$ {self.valor} - {self.vencimento.strftime('%d/%m/%Y')} ({status})"
    
    @property
    def dias_vencimento(self):
        """Calcula dias até vencimento (negativo se vencido)"""
        from datetime import date
        return (self.vencimento - date.today()).days
    
    @property
    def em_atraso(self):
        """Retorna True se vencida e não paga"""
        from datetime import date
        return not self.pago and self.vencimento < date.today()


class ContaReceber(models.Model):
    """Registro de contas a receber (será importado de outro módulo)"""
    
    CLASSIFICACAO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DEVOLUCAO', 'Devolução'),
    ]
    
    conta = models.ForeignKey(PlanoConta, on_delete=models.PROTECT, related_name='contas_receber_principais', verbose_name='Conta Principal')
    subconta = models.ForeignKey(PlanoConta, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_receber_subcontas', verbose_name='Subconta')
    
    cliente = models.CharField(max_length=255, verbose_name='Cliente')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    vencimento = models.DateField(verbose_name='Data de Vencimento')
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor')
    
    data_recebimento = models.DateField(null=True, blank=True, verbose_name='Data de Recebimento')
    valor_recebido = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor Recebido')
    juros = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Juros')
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Desconto')
    
    recebido_atrasado = models.BooleanField(default=False, verbose_name='Recebido Atrasado')
    recebido = models.BooleanField(default=False, verbose_name='Recebido')
    
    conta_financeira = models.ForeignKey(ContaFinanceira, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Conta Financeira')
    metodo_pagamento = models.ForeignKey(MetodoPagamento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Método de Recebimento')
    classificacao = models.CharField(max_length=15, choices=CLASSIFICACAO_CHOICES, default='RECEITA', verbose_name='Classificação')
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_receber')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['-vencimento']
        indexes = [
            models.Index(fields=['vencimento']),
            models.Index(fields=['recebido']),
            models.Index(fields=['cliente']),
        ]
    
    def __str__(self):
        status = "✓ Recebido" if self.recebido else "⟳ Pendente"
        return f"{self.cliente} - R$ {self.valor} - {self.vencimento.strftime('%d/%m/%Y')} ({status})"
    
    def save(self, *args, **kwargs):
        if self.cliente:
            self.cliente = self.cliente.upper().strip()
        if self.descricao:
            self.descricao = self.descricao.upper().strip()
        super().save(*args, **kwargs)
    
    @property
    def dias_vencimento(self):
        """Calcula dias até vencimento (negativo se vencido)"""
        from datetime import date
        return (self.vencimento - date.today()).days
    
    @property
    def em_atraso(self):
        """Retorna True se vencida e não recebida"""
        from datetime import date
        return not self.recebido and self.vencimento < date.today()


class MovimentacaoFinanceira(models.Model):
    """Movimentações da conta corrente das instituições financeiras"""
    
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]
    
    ORIGEM_CHOICES = [
        ('MANUAL', 'Lançamento Manual'),
        ('CONTA_PAGAR', 'Conta a Pagar'),
        ('CONTA_RECEBER', 'Conta a Receber'),
        ('TRANSFERENCIA', 'Transferência'),
    ]
    
    conta_financeira = models.ForeignKey(
        ContaFinanceira, 
        on_delete=models.PROTECT, 
        related_name='movimentacoes',
        verbose_name='Conta Financeira'
    )
    
    data = models.DateField(verbose_name='Data')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    
    descricao = models.TextField(verbose_name='Descrição')
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='MANUAL', verbose_name='Origem')
    
    # Referências opcionais para rastreamento
    conta_pagar = models.ForeignKey(
        ContaPagar, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimentacoes',
        verbose_name='Conta a Pagar'
    )
    conta_receber = models.ForeignKey(
        ContaReceber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimentacoes',
        verbose_name='Conta a Receber'
    )
    
    # Para transferências entre contas
    conta_destino = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transferencias_recebidas',
        verbose_name='Conta Destino'
    )
    
    categoria = models.ForeignKey(
        PlanoConta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoria'
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimentacoes_financeiras'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Movimentação Financeira'
        verbose_name_plural = 'Movimentações Financeiras'
        ordering = ['-data', '-criado_em']
        indexes = [
            models.Index(fields=['conta_financeira', '-data']),
            models.Index(fields=['tipo']),
            models.Index(fields=['data']),
        ]
    
    def __str__(self):
        simbolo = "+" if self.tipo == 'ENTRADA' else "-"
        return f"{self.conta_financeira.nome} - {simbolo}R$ {self.valor} - {self.data.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # Auto-capitalizar descrição
        if self.descricao:
            self.descricao = self.descricao.strip()
        super().save(*args, **kwargs)

from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Cliente(models.Model):
    nome = models.CharField(max_length=200, verbose_name='Nome/Razão Social')
    cpf_cnpj = models.CharField(max_length=20, unique=True, verbose_name='CPF/CNPJ')
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.cpf_cnpj})"


class OrigemCobranca(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome da Origem')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Origem de Cobrança'
        verbose_name_plural = 'Origens de Cobrança'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class NotaFiscal(models.Model):
    numero_nota = models.CharField(max_length=20, verbose_name='Número da NF')
    numero_pedido = models.CharField(max_length=20, blank=True, null=True, verbose_name='Número do Pedido')
    serie = models.CharField(max_length=10, blank=True, null=True, verbose_name='Série')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='notas_fiscais')
    data_emissao = models.DateTimeField(verbose_name='Data de Emissão')
    data_vencimento = models.DateField(blank=True, null=True, verbose_name='Data de Vencimento')
    
    valor_produtos = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor dos Produtos')
    valor_ipi = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor do IPI')
    valor_desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor de Desconto')
    valor_acrescimo = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor de Acréscimo')
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Total')
    
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota Fiscal'
        verbose_name_plural = 'Notas Fiscais'
        ordering = ['-data_emissao']
        unique_together = ['numero_nota', 'serie']

    def __str__(self):
        return f"NF {self.numero_nota} - {self.cliente.nome}"

    @property
    def valor_carteira(self):
        """Valor da carteira (produtos - IPI)"""
        return self.valor_produtos - self.valor_ipi

    @property
    def total_com_carteira(self):
        """Total NF + Carteira"""
        return self.valor_carteira + self.valor_total


class Parcela(models.Model):
    valor_original = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Valor Original da Parcela')
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('parcial', 'Pago Parcial'),
        ('em_negociacao', 'Em Negociação'),
        ('cancelado', 'Cancelado'),
    ]

    TIPO_CHOICES = [
        ('NF', 'Nota Fiscal'),
        ('CARTEIRA', 'Carteira'),
    ]

    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.PROTECT, related_name='parcelas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='parcelas')
    origem = models.ForeignKey(OrigemCobranca, on_delete=models.SET_NULL, null=True, blank=True)
    conta_financeira = models.ForeignKey('cadastros.ContaFinanceira', on_delete=models.SET_NULL, 
                                        null=True, blank=True, related_name='parcelas_receber',
                                        verbose_name='Instituição Financeira')
    
    tipo_parcela = models.CharField(max_length=10, choices=TIPO_CHOICES, default='NF', verbose_name='Tipo')
    numero_parcela = models.IntegerField(verbose_name='Número da Parcela')
    codigo_identificador = models.CharField(max_length=50, unique=True, blank=True, null=True, 
                                           verbose_name='Código Identificador')
    
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor da Parcela')
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor Pago')
    desconto_concedido = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Desconto')
    juros = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Juros')
    multa = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Multa')
    acrescimos = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Acréscimos')
    
    data_vencimento = models.DateField(verbose_name='Data de Vencimento')
    data_pagamento = models.DateField(blank=True, null=True, verbose_name='Data de Pagamento')
    
    status_pagamento = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente',
                                       verbose_name='Status')
    motivo_desconto = models.CharField(max_length=200, blank=True, null=True, verbose_name='Motivo do Desconto')
    observacao = models.TextField(blank=True, null=True, verbose_name='Observações')
    
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['data_vencimento', 'numero_parcela']

    def __str__(self):
        return f"{self.codigo_identificador or f'Parcela {self.numero_parcela}'} - {self.cliente.nome}"

    def save(self, *args, **kwargs):
        # Gerar código identificador automaticamente se não existir
        if not self.codigo_identificador:
            tipo = self.tipo_parcela
            nf = self.nota_fiscal.numero_nota
            num = str(self.numero_parcela).zfill(2)
            self.codigo_identificador = f"{tipo}-{nf}-P{num}"
        # Preencher valor_original se não existir
        if self.valor_original is None:
            self.valor_original = self.valor
        super().save(*args, **kwargs)

    @property
    def esta_quitada(self):
        """Verifica se a parcela está quitada"""
        return self.status_pagamento == 'pago'

    @property
    def esta_em_atraso(self):
        """Verifica se a parcela está em atraso"""
        from datetime import date
        return (not self.esta_quitada and 
                self.data_vencimento < date.today() and 
                self.status_pagamento == 'pendente')

    @property
    def total_a_pagar(self):
        """Calcula o total a pagar (valor + juros + multa + acréscimos - desconto)"""
        return (self.valor + self.juros + self.multa + 
                self.acrescimos - self.desconto_concedido)

    @property
    def saldo_restante(self):
        """Calcula o saldo restante a pagar"""
        return self.total_a_pagar - self.valor_pago


class CreditoCobranca(models.Model):
    STATUS_CHOICES = [
        ('solicitado', 'Solicitado'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('utilizado', 'Utilizado'),
    ]

    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.PROTECT, related_name='creditos')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='creditos')
    
    valor_credito = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Solicitado')
    valor_aprovado = models.DecimalField(max_digits=15, decimal_places=2, default=0, 
                                         verbose_name='Valor Aprovado')
    valor_utilizado = models.DecimalField(max_digits=15, decimal_places=2, default=0, 
                                         verbose_name='Valor Utilizado')
    
    justificativa = models.TextField(verbose_name='Justificativa da Solicitação')
    justificativa_aprovacao = models.TextField(blank=True, null=True, 
                                               verbose_name='Justificativa da Aprovação')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solicitado')
    
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação')
    data_liberacao = models.DateTimeField(blank=True, null=True, verbose_name='Data da Liberação')
    data_utilizacao = models.DateTimeField(blank=True, null=True, verbose_name='Data da Utilização')
    
    usuario_solicitante = models.CharField(max_length=100, blank=True, null=True)
    usuario_aprovador = models.CharField(max_length=100, blank=True, null=True)
    
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Crédito de Cobrança'
        verbose_name_plural = 'Créditos de Cobrança'
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f"Crédito NF {self.nota_fiscal.numero_nota} - R$ {self.valor_credito}"

    @property
    def saldo_disponivel(self):
        """Retorna o saldo disponível do crédito aprovado"""
        return self.valor_aprovado - self.valor_utilizado


class NotaFiscalCalculada(models.Model):
    """Model para armazenar dados importados do sistema Futura"""
    nro_nota_fiscal = models.IntegerField(verbose_name='Número NF')
    idreceita = models.IntegerField(verbose_name='ID Receita')
    valor_total_nf_futura = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Total NF')
    
    id_parcela = models.CharField(max_length=20, verbose_name='ID Parcela')
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor Parcela')
    
    chk_carteira = models.BooleanField(default=False, verbose_name='Carteira')
    chk_nf = models.BooleanField(default=False, verbose_name='NF')
    
    juros_perc = models.DecimalField(max_digits=6, decimal_places=4, default=0, verbose_name='Juros %')
    valor_juros = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Valor Juros')
    desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Desconto')
    multa = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Multa')
    pagto_total_parcela = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Pagto Total')
    
    vencimento_parcela = models.DateField(blank=True, null=True, verbose_name='Vencimento')
    data_pagto_parcela = models.DateField(blank=True, null=True, verbose_name='Data Pagamento')
    
    id_banco = models.IntegerField(verbose_name='ID Banco')
    banco = models.CharField(max_length=100, verbose_name='Banco')
    
    cnpj_cpf = models.CharField(max_length=20, verbose_name='CNPJ/CPF')
    cliente = models.CharField(max_length=200, verbose_name='Cliente')
    
    data_emissao_futura = models.DateField(blank=True, null=True, verbose_name='Data Emissão')
    usuario = models.CharField(max_length=100, verbose_name='Usuário')
    data_cadastro = models.DateField(blank=True, null=True, verbose_name='Data Cadastro')
    data_hora_importacao = models.DateTimeField(auto_now_add=True, verbose_name='Importado em')

    class Meta:
        verbose_name = 'Nota Fiscal Calculada (Futura)'
        verbose_name_plural = 'Notas Fiscais Calculadas (Futura)'
        ordering = ['-data_hora_importacao']

    def __str__(self):
        return f"NF {self.nro_nota_fiscal} - Parcela {self.id_parcela}"


class HistoricoNegociacao(models.Model):
    """Histórico de negociações de parcelas com pagamento parcial"""
    
    # Parcela que recebeu pagamento parcial e virou -N
    parcela_negociada = models.ForeignKey(
        Parcela, 
        on_delete=models.PROTECT, 
        related_name='negociacao',
        verbose_name='Parcela Negociada'
    )
    
    # Valores
    valor_original = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Original'
    )
    valor_pago = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Valor Pago'
    )
    saldo_renegociado = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name='Saldo Renegociado'
    )
    juros_negociacao = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=0,
        verbose_name='Juros da Negociação'
    )
    quantidade_parcelas = models.IntegerField(
        verbose_name='Quantidade de Parcelas Geradas'
    )
    
    # Negociação consolidada
    is_consolidada = models.BooleanField(
        default=False,
        verbose_name='Negociação Consolidada'
    )
    parcelas_consolidadas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Códigos das Parcelas Consolidadas',
        help_text='IDs das parcelas separados por vírgula'
    )
    
    # Parcelas geradas (A, B, C...)
    # Será populado via código após criar as parcelas
    
    # Rastreabilidade
    observacao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Observação'
    )
    usuario = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        verbose_name='Usuário'
    )
    data_negociacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Negociação'
    )
    
    class Meta:
        verbose_name = 'Histórico de Negociação'
        verbose_name_plural = 'Históricos de Negociações'
        ordering = ['-data_negociacao']
    
    def __str__(self):
        return f"Negociação {self.parcela_negociada.codigo_identificador} - {self.data_negociacao.strftime('%d/%m/%Y')}"
    
    def get_parcelas_geradas(self):
        """Retorna as parcelas geradas a partir desta negociação"""
        # Busca parcelas com código base + sufixo A, B, C...
        codigo_base = self.parcela_negociada.codigo_identificador.replace('-N', '')
        return Parcela.objects.filter(
            codigo_identificador__startswith=codigo_base + '-',
            cliente=self.parcela_negociada.cliente
        ).exclude(id=self.parcela_negociada.id).order_by('numero_parcela')

from django.db import models
from django.contrib.auth.models import User


class ConfiguracaoFirebird(models.Model):
    """Configuração da conexão com Firebird do Futura"""
    
    host = models.CharField(max_length=100, default='45.178.23.26', verbose_name='IP/Host do Servidor')
    port = models.IntegerField(default=3050, verbose_name='Porta')
    database = models.CharField(max_length=200, default='c:/FuturaDados/DADOS.FDB', verbose_name='Caminho do Banco')
    user = models.CharField(max_length=100, default='SYS_CONSULTA', verbose_name='Usuário')
    password = models.CharField(max_length=100, default='futura1212', verbose_name='Senha')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Configuração Firebird'
        verbose_name_plural = 'Configurações Firebird'
        
    def __str__(self):
        return f"Firebird - {self.host}:{self.port}"
    
    @classmethod
    def get_config(cls):
        """Retorna a primeira configuração ativa, ou cria uma padrão"""
        config = cls.objects.filter(ativo=True).first()
        if not config:
            config, _ = cls.objects.get_or_create(pk=1)
        return config


class ImportacaoLog(models.Model):
    """Log de todas as importações realizadas"""
    
    TIPO_CHOICES = [
        ('cadastro', 'Cadastros'),
        ('nota_fiscal', 'Notas Fiscais'),
        ('conta_parcela', 'Parcelas de Contas'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_progresso', 'Em Progresso'),
        ('concluida', 'Concluída'),
        ('erro', 'Erro'),
    ]
    
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente')
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Estatísticas
    total_registros = models.IntegerField(default=0)
    registros_criados = models.IntegerField(default=0)
    registros_atualizados = models.IntegerField(default=0)
    registros_erro = models.IntegerField(default=0)
    
    # Detalhes
    mensagem = models.TextField(null=True, blank=True)
    erros_detalhe = models.JSONField(default=list, blank=True)
    
    # Filtros de data usados
    data_inicial_filtro = models.DateField(null=True, blank=True)
    data_final_filtro = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'importacao_log'
        ordering = ['-data_inicio']
        verbose_name = 'Log de Importação'
        verbose_name_plural = 'Logs de Importação'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.get_status_display()} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"


class CadastroFutura(models.Model):
    """Cadastros importados do Futura (clientes, fornecedores, etc)"""
    
    SIM_NAO_CHOICES = [('S', 'Sim'), ('N', 'Não')]
    
    id = models.IntegerField(primary_key=True)
    razao_social = models.CharField(max_length=80, null=True, blank=True)
    fantasia = models.CharField(max_length=80, null=True, blank=True)
    cnpj_cpf = models.CharField(max_length=18, null=True, blank=True, db_index=True)
    inscricao_rg = models.CharField(max_length=20, null=True, blank=True)
    
    # Flags de tipo
    chk_cliente = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    chk_fornecedor = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    chk_funcionario = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    chk_transportadora = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    chk_empresa = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    chk_vendedor = models.CharField(max_length=1, choices=SIM_NAO_CHOICES, null=True, blank=True)
    
    # Contato
    e_mail = models.EmailField(max_length=90, null=True, blank=True)
    e_mail_alternativo = models.EmailField(max_length=90, null=True, blank=True)
    
    # Dados comerciais
    limite_compra_funcionario = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    limite_venda_valor = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    limite_desconto_percentual = models.DecimalField(max_digits=15, decimal_places=5, null=True, blank=True)
    
    # Referências
    fk_vendedor = models.IntegerField(null=True, blank=True)
    fk_transportadora = models.IntegerField(null=True, blank=True)
    fk_empresa = models.IntegerField(null=True, blank=True)
    
    # Dados
    data_cadastro = models.DateTimeField(null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)
    
    # Controle de importação
    importacao_log = models.ForeignKey(ImportacaoLog, on_delete=models.SET_NULL, null=True, blank=True, related_name='cadastros')
    sincronizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'importacao_cadastro_futura'
        verbose_name = 'Cadastro do Futura'
        verbose_name_plural = 'Cadastros do Futura'
    
    def __str__(self):
        return f"{self.razao_social or self.fantasia or f'ID: {self.id}'}"


class NotaFiscalFutura(models.Model):
    """Notas fiscais importadas do Futura"""
    
    id = models.IntegerField(primary_key=True)
    nro_nota = models.IntegerField(db_index=True)
    serie = models.CharField(max_length=3, null=True, blank=True)
    
    # Referências
    fk_empresa = models.IntegerField(null=True, blank=True)
    fk_cadastro = models.IntegerField(null=True, blank=True)
    fk_pedido = models.IntegerField(null=True, blank=True)
    fk_transportadora = models.IntegerField(null=True, blank=True)
    fk_vendedor = models.IntegerField(null=True, blank=True)
    
    # Datas
    data_emissao = models.DateField(null=True, blank=True, db_index=True)
    data_saida_entrada = models.DateField(null=True, blank=True)
    data_competencia = models.DateField(null=True, blank=True)
    data_hora_emissao = models.DateTimeField(null=True, blank=True)
    
    # Valores
    total_produto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_frete = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_acrescimo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_nota = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Impostos
    total_icms_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_ipi_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_tributos_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Dados adicionais
    quantidade = models.IntegerField(null=True, blank=True)
    especie = models.CharField(max_length=60, null=True, blank=True)
    placa = models.CharField(max_length=8, null=True, blank=True)
    status = models.SmallIntegerField(null=True, blank=True)
    entrada_saida = models.CharField(max_length=1, null=True, blank=True)
    
    # CNPJ do cliente
    cnpj_cpf_cliente = models.CharField(max_length=18, null=True, blank=True)
    
    # Observações
    observacao_1 = models.TextField(null=True, blank=True)
    observacao_2 = models.TextField(null=True, blank=True)
    
    # Controle de importação
    importacao_log = models.ForeignKey(ImportacaoLog, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_fiscais')
    sincronizado_em = models.DateTimeField(auto_now=True)

    # Marcação para controle de lançamento de parcelas
    parcelas_lancadas = models.BooleanField(default=False, verbose_name='Parcelas já lançadas')
    
    class Meta:
        db_table = 'importacao_nota_fiscal_futura'
        verbose_name = 'Nota Fiscal do Futura'
        verbose_name_plural = 'Notas Fiscais do Futura'
        indexes = [
            models.Index(fields=['data_emissao']),
            models.Index(fields=['nro_nota', 'serie']),
        ]
    
    def __str__(self):
        return f"NF {self.nro_nota}/{self.serie} - {self.data_emissao}"


class ContaParcelaFutura(models.Model):
    """Parcelas de contas importadas do Futura"""
    
    id = models.IntegerField(primary_key=True)
    fk_conta = models.IntegerField(null=True, blank=True)
    fk_nota_fiscal = models.IntegerField(null=True, blank=True)
    
    # Documento
    documento = models.CharField(max_length=20, null=True, blank=True)
    nosso_numero = models.CharField(max_length=20, null=True, blank=True)
    
    # Datas
    data_vencimento = models.DateField(null=True, blank=True, db_index=True)
    
    # Valores
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_multa = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    valor_juros = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Status
    status = models.SmallIntegerField(null=True, blank=True)
    dias_atraso = models.IntegerField(null=True, blank=True)
    
    # Boleto/PIX
    boleto_codigo_barras = models.CharField(max_length=100, null=True, blank=True)
    boleto_linha_digitavel = models.CharField(max_length=100, null=True, blank=True)
    boleto_qrcode_pix = models.CharField(max_length=300, null=True, blank=True)
    
    # Controle de importação
    importacao_log = models.ForeignKey(ImportacaoLog, on_delete=models.SET_NULL, null=True, blank=True, related_name='parcelas')
    sincronizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'importacao_conta_parcela_futura'
        verbose_name = 'Parcela do Futura'
        verbose_name_plural = 'Parcelas do Futura'
        indexes = [
            models.Index(fields=['data_vencimento']),
        ]
    
    def __str__(self):
        return f"Parcela {self.documento} - Vencimento: {self.data_vencimento}"

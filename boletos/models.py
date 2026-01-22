from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from contas_receber.models import Cliente, Parcela
from cadastros.models import ContaFinanceira


class ConfiguracaoBancaria(models.Model):
    """
    Configuração dos dados bancários para emissão de boletos
    Baseado nas especificações da Caixa Econômica Federal (Banco 104)
    """
    # Vinculação com Conta Financeira (opcional)
    conta_financeira = models.ForeignKey(ContaFinanceira, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        verbose_name='Conta Financeira',
                                        help_text='Vincular a uma conta financeira cadastrada')
    
    # Identificação
    nome = models.CharField('Nome da Configuração', max_length=100)
    ativo = models.BooleanField('Ativo', default=True)
    
    # Dados do Banco
    codigo_banco = models.CharField('Código do Banco', max_length=3, default='104', 
                                   help_text='104 = Caixa Econômica Federal')
    
    # Dados do Beneficiário (Cedente)
    codigo_beneficiario = models.CharField('Código do Beneficiário', max_length=20,
                                          blank=True, null=True,
                                          help_text='Fornecido pela Caixa')
    agencia = models.CharField('Agência', max_length=5, blank=True, null=True)
    agencia_dv = models.CharField('DV Agência', max_length=1, blank=True, null=True)
    conta = models.CharField('Conta Corrente', max_length=12, blank=True, null=True)
    conta_dv = models.CharField('DV Conta', max_length=1, blank=True, null=True)
    
    # Dados da Cobrança
    carteira = models.CharField('Carteira', max_length=2, default='1', blank=True,
                               help_text='Carteira de cobrança. Padrão: 1')
    modalidade = models.CharField('Modalidade', max_length=2, default='14', blank=True,
                                 help_text='Modalidade de cobrança. Comum: 14')
    convenio = models.CharField('Número do Convênio', max_length=20, blank=True, null=True,
                               help_text='Número do convênio de cobrança')
    
    # Controle do Nosso Número
    nosso_numero_inicio = models.BigIntegerField('Nosso Número Inicial', default=1,
                                                validators=[MinValueValidator(1)])
    nosso_numero_atual = models.BigIntegerField('Nosso Número Atual', default=1,
                                               validators=[MinValueValidator(1)])
    nosso_numero_fim = models.BigIntegerField('Nosso Número Final', blank=True, null=True,
                                             validators=[MinValueValidator(1)])
    
    # Dados da Empresa
    razao_social = models.CharField('Razão Social', max_length=100, blank=True, null=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True, null=True)
    endereco = models.CharField('Endereço', max_length=200, blank=True, null=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    uf = models.CharField('UF', max_length=2, blank=True, null=True)
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    
    # Configurações de Juros e Multa
    percentual_juros_mes = models.DecimalField('Juros ao Mês (%)', max_digits=5, decimal_places=2,
                                              default=Decimal('0.00'),
                                              validators=[MinValueValidator(Decimal('0')),
                                                        MaxValueValidator(Decimal('100'))])
    percentual_multa = models.DecimalField('Multa (%)', max_digits=5, decimal_places=2,
                                          default=Decimal('0.00'),
                                          validators=[MinValueValidator(Decimal('0')),
                                                    MaxValueValidator(Decimal('100'))])
    dias_para_multa = models.IntegerField('Dias para Aplicar Multa', default=1,
                                         validators=[MinValueValidator(1)])
    
    # Configurações de Protesto
    dias_para_protesto = models.IntegerField('Dias para Protesto', default=0,
                                            help_text='0 = Não protestar')
    dias_para_baixa = models.IntegerField('Dias para Baixa Automática', default=0,
                                         help_text='0 = Não baixar automaticamente')
    
    # Mensagens Padrão
    instrucao1 = models.CharField('Instrução 1', max_length=100, blank=True,
                                 default='Não receber após o vencimento')
    instrucao2 = models.CharField('Instrução 2', max_length=100, blank=True)
    instrucao3 = models.CharField('Instrução 3', max_length=100, blank=True)
    local_pagamento = models.CharField('Local de Pagamento', max_length=100,
                                      default='PREFERENCIALMENTE NAS CASAS LOTÉRICAS ATÉ O VALOR LIMITE')
    
    # Sequenciais para CNAB
    sequencial_arquivo = models.IntegerField('Sequencial do Arquivo', default=1,
                                            validators=[MinValueValidator(1)])
    sequencial_lote = models.IntegerField('Sequencial do Lote', default=1,
                                         validators=[MinValueValidator(1)])
    
    # Timestamps
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração Bancária'
        verbose_name_plural = 'Configurações Bancárias'
        ordering = ['-ativo', 'nome']
    
    def __str__(self):
        return f"{self.nome} - Ag: {self.agencia} Conta: {self.conta}-{self.conta_dv}"
    
    @property
    def nome_exibicao(self):
        """Nome para exibição em formulários"""
        if self.conta_financeira:
            return f"{self.nome} ({self.conta_financeira.nome})"
        return self.nome
    
    def proximo_nosso_numero(self):
        """Retorna o próximo nosso número disponível e incrementa o contador"""
        if self.nosso_numero_fim and self.nosso_numero_atual >= self.nosso_numero_fim:
            raise ValueError('Nosso número esgotado! Configure novos limites.')
        
        numero = self.nosso_numero_atual
        self.nosso_numero_atual += 1
        self.save(update_fields=['nosso_numero_atual'])
        return numero


class Boleto(models.Model):
    """
    Representa um boleto bancário emitido
    """
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Emissão'),
        ('EMITIDO', 'Emitido'),
        ('REGISTRADO', 'Registrado no Banco'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado'),
        ('VENCIDO', 'Vencido'),
    ]
    
    # Relacionamentos
    configuracao = models.ForeignKey(ConfiguracaoBancaria, on_delete=models.PROTECT,
                                    verbose_name='Configuração Bancária')
    parcela = models.OneToOneField(Parcela, on_delete=models.CASCADE,
                                   verbose_name='Parcela', related_name='boleto')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT,
                               verbose_name='Cliente/Pagador')
    
    # Identificação do Boleto
    nosso_numero = models.CharField('Nosso Número', max_length=17, unique=True)
    numero_documento = models.CharField('Número do Documento', max_length=20)
    
    # Valores
    valor_documento = models.DecimalField('Valor do Documento', max_digits=15, decimal_places=2)
    valor_desconto = models.DecimalField('Valor do Desconto', max_digits=15, decimal_places=2,
                                        default=Decimal('0.00'))
    valor_abatimento = models.DecimalField('Valor do Abatimento', max_digits=15, decimal_places=2,
                                          default=Decimal('0.00'))
    valor_mora_dia = models.DecimalField('Valor Mora/Dia', max_digits=15, decimal_places=2,
                                        default=Decimal('0.00'))
    valor_multa = models.DecimalField('Valor da Multa', max_digits=15, decimal_places=2,
                                     default=Decimal('0.00'))
    
    # Datas
    data_emissao = models.DateField('Data de Emissão')
    data_vencimento = models.DateField('Data de Vencimento')
    data_limite_pagamento = models.DateField('Data Limite para Pagamento', null=True, blank=True)
    data_desconto = models.DateField('Data Limite para Desconto', null=True, blank=True)
    
    # Código de Barras
    codigo_barras = models.CharField('Código de Barras', max_length=44, blank=True)
    linha_digitavel = models.CharField('Linha Digitável', max_length=54, blank=True)
    
    # Status e Controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    enviado_banco = models.BooleanField('Enviado ao Banco', default=False)
    data_envio_banco = models.DateTimeField('Data de Envio ao Banco', null=True, blank=True)
    
    # Instruções
    instrucao1 = models.CharField('Instrução 1', max_length=100, blank=True)
    instrucao2 = models.CharField('Instrução 2', max_length=100, blank=True)
    mensagem_sacador = models.TextField('Mensagem ao Sacador', blank=True,
                                       help_text='Demonstrativo/Descrição do título')
    
    # Timestamps
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Boleto'
        verbose_name_plural = 'Boletos'
        ordering = ['-data_vencimento', '-criado_em']
        indexes = [
            models.Index(fields=['nosso_numero']),
            models.Index(fields=['status']),
            models.Index(fields=['data_vencimento']),
        ]
    
    def __str__(self):
        return f"Boleto {self.nosso_numero} - {self.cliente.nome} - R$ {self.valor_documento}"
    
    def save(self, *args, **kwargs):
        # Se é um novo boleto, gera o nosso número
        if not self.pk and not self.nosso_numero:
            from .utils.codigo_barras import gerar_nosso_numero
            self.nosso_numero = gerar_nosso_numero(self.configuracao)
        
        # Gera código de barras e linha digitável se ainda não existem
        if not self.codigo_barras or not self.linha_digitavel:
            from .utils.codigo_barras import gerar_codigo_barras, gerar_linha_digitavel
            self.codigo_barras = gerar_codigo_barras(self)
            self.linha_digitavel = gerar_linha_digitavel(self.codigo_barras)
        
        super().save(*args, **kwargs)


class RemessaCNAB(models.Model):
    """
    Representa um arquivo de remessa CNAB enviado ao banco
    """
    TIPO_CHOICES = [
        ('CNAB240', 'CNAB 240'),
        ('CNAB400', 'CNAB 400'),
    ]
    
    STATUS_CHOICES = [
        ('GERADO', 'Gerado'),
        ('ENVIADO', 'Enviado'),
        ('PROCESSADO', 'Processado pelo Banco'),
        ('ERRO', 'Erro no Processamento'),
    ]
    
    # Identificação
    configuracao = models.ForeignKey(ConfiguracaoBancaria, on_delete=models.PROTECT,
                                    verbose_name='Configuração Bancária')
    numero_sequencial = models.IntegerField('Número Sequencial')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES, default='CNAB240')
    
    # Arquivo
    nome_arquivo = models.CharField('Nome do Arquivo', max_length=255)
    conteudo = models.TextField('Conteúdo do Arquivo')
    
    # Boletos incluídos
    boletos = models.ManyToManyField(Boleto, verbose_name='Boletos', related_name='remessas')
    quantidade_titulos = models.IntegerField('Quantidade de Títulos', default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=15, decimal_places=2,
                                     default=Decimal('0.00'))
    
    # Status e Controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='GERADO')
    data_geracao = models.DateTimeField('Data de Geração', auto_now_add=True)
    data_envio = models.DateTimeField('Data de Envio', null=True, blank=True)
    
    # Retorno
    arquivo_retorno = models.TextField('Arquivo de Retorno', blank=True)
    data_processamento = models.DateTimeField('Data de Processamento', null=True, blank=True)
    mensagem_erro = models.TextField('Mensagem de Erro', blank=True)
    
    class Meta:
        verbose_name = 'Remessa CNAB'
        verbose_name_plural = 'Remessas CNAB'
        ordering = ['-data_geracao']
        unique_together = [['configuracao', 'numero_sequencial']]
    
    def __str__(self):
        return f"Remessa {self.numero_sequencial} - {self.quantidade_titulos} títulos - {self.status}"


class RetornoCNAB(models.Model):
    """
    Representa um arquivo de retorno CNAB recebido do banco
    """
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Processamento'),
        ('PROCESSADO', 'Processado'),
        ('ERRO', 'Erro no Processamento'),
    ]
    
    # Identificação
    configuracao = models.ForeignKey(ConfiguracaoBancaria, on_delete=models.PROTECT,
                                    verbose_name='Configuração Bancária')
    remessa = models.ForeignKey(RemessaCNAB, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Remessa Relacionada')
    
    # Arquivo
    nome_arquivo = models.CharField('Nome do Arquivo', max_length=255)
    conteudo = models.TextField('Conteúdo do Arquivo')
    
    # Processamento
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_importacao = models.DateTimeField('Data de Importação', auto_now_add=True)
    data_processamento = models.DateTimeField('Data de Processamento', null=True, blank=True)
    
    quantidade_registros = models.IntegerField('Quantidade de Registros', default=0)
    quantidade_confirmados = models.IntegerField('Títulos Confirmados', default=0)
    quantidade_rejeitados = models.IntegerField('Títulos Rejeitados', default=0)
    quantidade_liquidados = models.IntegerField('Títulos Liquidados', default=0)
    
    # Erros
    mensagem_erro = models.TextField('Mensagens de Erro', blank=True)
    log_processamento = models.TextField('Log de Processamento', blank=True)
    
    class Meta:
        verbose_name = 'Retorno CNAB'
        verbose_name_plural = 'Retornos CNAB'
        ordering = ['-data_importacao']
    
    def __str__(self):
        return f"Retorno {self.nome_arquivo} - {self.status}"

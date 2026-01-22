from django.db import models
from django.contrib.auth.models import User

class PlanoConta(models.Model):
    """
    Compatível com tabela externa (id, nome, codigo, ativo, pai_id)
    - 'codigo' como texto para suportar formatos 1, 1.1, 2.3 etc
    - 'pai' referencia hierarquia; coluna no banco será 'pai_id'
    - 'id' pode ser definido manualmente durante importação
    """
    id = models.PositiveIntegerField(primary_key=True)
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20)
    ativo = models.BooleanField(default=True)
    pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='filhos')

    class Meta:
        verbose_name = 'Plano de Conta'
        verbose_name_plural = 'Plano de Contas'
        ordering = ['codigo', 'nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class ContaFinanceira(models.Model):
    """
    Contas de Banco/Factory com controle de saldo
    """
    TIPO_CHOICES = [
        ('banco', 'Banco'),
        ('factory', 'Factory'),
    ]
    nome = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    agencia_dv = models.CharField(max_length=1, blank=True, null=True, verbose_name='DV Agência')
    conta = models.CharField(max_length=30, blank=True, null=True)
    conta_dv = models.CharField(max_length=1, blank=True, null=True, verbose_name='DV Conta')
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Saldo Inicial')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conta Financeira'
        verbose_name_plural = 'Contas Financeiras'
        ordering = ['nome']

    def __str__(self):
        agencia_completa = f"{self.agencia}-{self.agencia_dv}" if self.agencia and self.agencia_dv else self.agencia or ""
        conta_completa = f"{self.conta}-{self.conta_dv}" if self.conta and self.conta_dv else self.conta or ""
        if agencia_completa and conta_completa:
            return f"{self.nome} (Ag: {agencia_completa} / Conta: {conta_completa})"
        return f"{self.nome} ({self.get_tipo_display()})"
    
    def saldo_atual(self):
        """Calcula o saldo atual baseado nas movimentações"""
        from financeiro.models import MovimentacaoFinanceira
        movimentacoes = MovimentacaoFinanceira.objects.filter(conta_financeira=self)
        
        entradas = sum(m.valor for m in movimentacoes if m.tipo == 'ENTRADA')
        saidas = sum(m.valor for m in movimentacoes if m.tipo == 'SAIDA')
        
        return self.saldo_inicial + entradas - saidas


class MetodoPagamento(models.Model):
    """
    Métodos de Pagamento (Dinheiro, PIX, Cartão, etc)
    """
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='metodos_pagamento')

    class Meta:
        verbose_name = 'Método de Pagamento'
        verbose_name_plural = 'Métodos de Pagamento'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    """
    Cadastro de Fornecedores
    """
    nome = models.CharField(max_length=200, unique=True)
    razao_social = models.CharField(max_length=200, blank=True, null=True)
    cnpj_cpf = models.CharField(max_length=18, blank=True, null=True, verbose_name='CNPJ/CPF')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=10, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fornecedores')

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        # Auto-uppercase no nome
        if self.nome:
            self.nome = self.nome.upper()
        if self.razao_social:
            self.razao_social = self.razao_social.upper()
        super().save(*args, **kwargs)

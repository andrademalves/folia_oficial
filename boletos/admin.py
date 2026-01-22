from django.contrib import admin
from .models import ConfiguracaoBancaria, Boleto, RemessaCNAB, RetornoCNAB


@admin.register(ConfiguracaoBancaria)
class ConfiguracaoBancariaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_banco', 'agencia', 'conta', 'codigo_beneficiario', 'ativo']
    list_filter = ['ativo', 'codigo_banco']
    search_fields = ['nome', 'razao_social', 'codigo_beneficiario']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'ativo')
        }),
        ('Dados Bancários', {
            'fields': ('codigo_banco', 'agencia', 'agencia_dv', 'conta', 'conta_dv',
                      'codigo_beneficiario', 'convenio', 'carteira', 'modalidade')
        }),
        ('Controle do Nosso Número', {
            'fields': ('nosso_numero_inicio', 'nosso_numero_atual', 'nosso_numero_fim')
        }),
        ('Dados da Empresa', {
            'fields': ('razao_social', 'cnpj', 'endereco', 'cidade', 'uf', 'cep')
        }),
        ('Configurações de Cobrança', {
            'fields': ('percentual_juros_mes', 'percentual_multa', 'dias_para_multa',
                      'dias_para_protesto', 'dias_para_baixa')
        }),
        ('Mensagens Padrão', {
            'fields': ('local_pagamento', 'instrucao1', 'instrucao2', 'instrucao3')
        }),
        ('Controle CNAB', {
            'fields': ('sequencial_arquivo', 'sequencial_lote')
        }),
    )


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ['nosso_numero', 'cliente', 'numero_documento', 'valor_documento', 
                   'data_vencimento', 'status', 'enviado_banco']
    list_filter = ['status', 'enviado_banco', 'data_vencimento', 'data_emissao']
    search_fields = ['nosso_numero', 'numero_documento', 'cliente__nome']
    date_hierarchy = 'data_vencimento'
    
    fieldsets = (
        ('Relacionamentos', {
            'fields': ('configuracao', 'parcela', 'cliente')
        }),
        ('Identificação', {
            'fields': ('nosso_numero', 'numero_documento')
        }),
        ('Valores', {
            'fields': ('valor_documento', 'valor_desconto', 'valor_abatimento',
                      'valor_mora_dia', 'valor_multa')
        }),
        ('Datas', {
            'fields': ('data_emissao', 'data_vencimento', 'data_limite_pagamento', 'data_desconto')
        }),
        ('Código de Barras', {
            'fields': ('codigo_barras', 'linha_digitavel'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'enviado_banco', 'data_envio_banco')
        }),
        ('Instruções', {
            'fields': ('instrucao1', 'instrucao2', 'mensagem_sacador'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['codigo_barras', 'linha_digitavel', 'data_envio_banco']


@admin.register(RemessaCNAB)
class RemessaCNABAdmin(admin.ModelAdmin):
    list_display = ['numero_sequencial', 'configuracao', 'tipo', 'quantidade_titulos',
                   'valor_total', 'status', 'data_geracao']
    list_filter = ['tipo', 'status', 'data_geracao']
    search_fields = ['nome_arquivo', 'numero_sequencial']
    date_hierarchy = 'data_geracao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('configuracao', 'numero_sequencial', 'tipo', 'nome_arquivo')
        }),
        ('Boletos', {
            'fields': ('boletos', 'quantidade_titulos', 'valor_total')
        }),
        ('Status', {
            'fields': ('status', 'data_geracao', 'data_envio', 'data_processamento')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'arquivo_retorno', 'mensagem_erro'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_geracao', 'quantidade_titulos', 'valor_total']


@admin.register(RetornoCNAB)
class RetornoCNABAdmin(admin.ModelAdmin):
    list_display = ['nome_arquivo', 'configuracao', 'status', 'quantidade_registros',
                   'quantidade_confirmados', 'quantidade_liquidados', 'data_importacao']
    list_filter = ['status', 'data_importacao']
    search_fields = ['nome_arquivo']
    date_hierarchy = 'data_importacao'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('configuracao', 'remessa', 'nome_arquivo')
        }),
        ('Processamento', {
            'fields': ('status', 'data_importacao', 'data_processamento')
        }),
        ('Estatísticas', {
            'fields': ('quantidade_registros', 'quantidade_confirmados',
                      'quantidade_rejeitados', 'quantidade_liquidados')
        }),
        ('Conteúdo', {
            'fields': ('conteudo', 'mensagem_erro', 'log_processamento'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_importacao']

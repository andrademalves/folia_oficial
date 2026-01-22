from django.contrib import admin
from .models import Cliente, NotaFiscal, OrigemCobranca, Parcela, CreditoCobranca, NotaFiscalCalculada, HistoricoNegociacao


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'email', 'telefone', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'estado', 'data_cadastro']
    search_fields = ['nome', 'cpf_cnpj', 'email']
    date_hierarchy = 'data_cadastro'


@admin.register(OrigemCobranca)
class OrigemCobrancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ['numero_nota', 'serie', 'cliente', 'data_emissao', 'valor_total', 'ativo']
    list_filter = ['ativo', 'data_emissao']
    search_fields = ['numero_nota', 'serie', 'cliente__nome', 'cliente__cpf_cnpj']
    date_hierarchy = 'data_emissao'
    raw_id_fields = ['cliente']


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ['codigo_identificador', 'nota_fiscal', 'cliente', 'numero_parcela', 
                    'valor', 'conta_financeira', 'data_vencimento', 'status_pagamento']
    list_filter = ['status_pagamento', 'tipo_parcela', 'conta_financeira', 'data_vencimento']
    search_fields = ['codigo_identificador', 'nota_fiscal__numero_nota', 'cliente__nome']
    date_hierarchy = 'data_vencimento'
    raw_id_fields = ['nota_fiscal', 'cliente', 'origem', 'conta_financeira']


@admin.register(CreditoCobranca)
class CreditoCobrancaAdmin(admin.ModelAdmin):
    list_display = ['nota_fiscal', 'cliente', 'valor_credito', 'valor_utilizado', 
                    'status', 'data_solicitacao', 'data_liberacao']
    list_filter = ['status', 'data_solicitacao', 'data_liberacao']
    search_fields = ['nota_fiscal__numero_nota', 'cliente__nome', 'justificativa']
    date_hierarchy = 'data_solicitacao'
    raw_id_fields = ['nota_fiscal', 'cliente']


@admin.register(NotaFiscalCalculada)
class NotaFiscalCalculadaAdmin(admin.ModelAdmin):
    list_display = ['nro_nota_fiscal', 'id_parcela', 'cliente', 'valor_parcela', 
                    'vencimento_parcela', 'data_pagto_parcela', 'data_hora_importacao']
    list_filter = ['data_hora_importacao', 'chk_carteira', 'chk_nf']
    search_fields = ['nro_nota_fiscal', 'cliente', 'cnpj_cpf']
    date_hierarchy = 'data_hora_importacao'
    readonly_fields = ['data_hora_importacao']


@admin.register(HistoricoNegociacao)
class HistoricoNegociacaoAdmin(admin.ModelAdmin):
    list_display = ['parcela_negociada', 'valor_original', 'valor_pago', 'saldo_renegociado',
                    'quantidade_parcelas', 'usuario', 'data_negociacao']
    list_filter = ['data_negociacao', 'usuario']
    search_fields = ['parcela_negociada__codigo_identificador', 'parcela_negociada__cliente__nome', 'observacao']
    date_hierarchy = 'data_negociacao'
    raw_id_fields = ['parcela_negociada', 'usuario']
    readonly_fields = ['data_negociacao']

from django.contrib import admin
from .models import ContaPagar, ContaReceber, MovimentacaoFinanceira


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ('fornecedor', 'conta', 'vencimento', 'valor', 'pago', 'classificacao', 'criado_em')
    list_filter = ('pago', 'classificacao', 'vencimento', 'criado_em')
    search_fields = ('fornecedor', 'conta__nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Informações Principais', {
            'fields': ('conta', 'subconta', 'fornecedor', 'descricao')
        }),
        ('Datas e Valores', {
            'fields': ('vencimento', 'valor', 'juros', 'desconto')
        }),
        ('Pagamento', {
            'fields': ('pago', 'data_pagamento', 'valor_pago', 'pago_atrasado')
        }),
        ('Relacionamentos', {
            'fields': ('conta_financeira', 'metodo_pagamento', 'classificacao')
        }),
        ('Auditoria', {
            'fields': ('usuario', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'conta', 'vencimento', 'valor', 'recebido', 'classificacao', 'criado_em')
    list_filter = ('recebido', 'classificacao', 'vencimento', 'criado_em')
    search_fields = ('cliente', 'conta__nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    fieldsets = (
        ('Informações Principais', {
            'fields': ('conta', 'subconta', 'cliente', 'descricao')
        }),
        ('Datas e Valores', {
            'fields': ('vencimento', 'valor', 'juros', 'desconto')
        }),
        ('Recebimento', {
            'fields': ('recebido', 'data_recebimento', 'valor_recebido', 'recebido_atrasado')
        }),
        ('Relacionamentos', {
            'fields': ('conta_financeira', 'metodo_pagamento', 'classificacao')
        }),
        ('Auditoria', {
            'fields': ('usuario', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(MovimentacaoFinanceira)
class MovimentacaoFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('conta_financeira', 'data', 'tipo', 'valor', 'origem')
    list_filter = ('tipo', 'origem', 'data', 'conta_financeira')
    search_fields = ('descricao',)
    readonly_fields = ('criado_em', 'atualizado_em')
    date_hierarchy = 'data'

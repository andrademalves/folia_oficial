from django.contrib import admin
from .models import PlanoConta, ContaFinanceira, MetodoPagamento, Fornecedor

@admin.register(PlanoConta)
class PlanoContaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nome', 'ativo', 'pai')
    list_filter = ('ativo',)
    search_fields = ('codigo', 'nome')

@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'agencia', 'conta', 'ativo')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'agencia', 'conta')

@admin.register(MetodoPagamento)
class MetodoPagamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'ativo', 'usuario', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj_cpf', 'telefone', 'email', 'cidade', 'estado', 'ativo', 'criado_em')
    list_filter = ('ativo', 'estado')
    search_fields = ('nome', 'razao_social', 'cnpj_cpf', 'email')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'razao_social', 'cnpj_cpf')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco', 'cidade', 'estado', 'cep')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Status e Controle', {
            'fields': ('ativo', 'usuario')
        }),
    )
    readonly_fields = ()
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import ImportacaoLog, CadastroFutura, NotaFiscalFutura, ContaParcelaFutura, ConfiguracaoFirebird


@admin.register(ConfiguracaoFirebird)
class ConfiguracaoFirebirdAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'user', 'ativo', 'atualizado_em')
    fields = ('host', 'port', 'database', 'user', 'password', 'ativo')
    readonly_fields = ('criado_em', 'atualizado_em')
    
    def has_add_permission(self, request):
        # Permite apenas uma configuração ativa
        return not ConfiguracaoFirebird.objects.filter(ativo=True).exists()


@admin.register(ImportacaoLog)
class ImportacaoLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_tipo_display', 'get_status_display', 'usuario', 'data_inicio', 'registros_criados', 'registros_erro')
    list_filter = ('tipo', 'status', 'data_inicio')
    search_fields = ('usuario__username', 'mensagem')
    readonly_fields = ('data_inicio', 'data_fim')


@admin.register(CadastroFutura)
class CadastroFuturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'razao_social', 'cnpj_cpf', 'chk_cliente', 'chk_fornecedor', 'sincronizado_em')
    list_filter = ('chk_cliente', 'chk_fornecedor', 'chk_funcionario', 'sincronizado_em')
    search_fields = ('razao_social', 'fantasia', 'cnpj_cpf')
    readonly_fields = ('id', 'sincronizado_em')


@admin.register(NotaFiscalFutura)
class NotaFiscalFuturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nro_nota', 'serie', 'data_emissao', 'total_nota', 'sincronizado_em')
    list_filter = ('data_emissao', 'status', 'sincronizado_em')
    search_fields = ('nro_nota', 'serie')
    readonly_fields = ('id', 'sincronizado_em')


@admin.register(ContaParcelaFutura)
class ContaParcelaFuturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'documento', 'data_vencimento', 'valor_parcela', 'status', 'sincronizado_em')
    list_filter = ('data_vencimento', 'status', 'sincronizado_em')
    search_fields = ('documento', 'nosso_numero')
    readonly_fields = ('id', 'sincronizado_em')

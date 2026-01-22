from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Modulo, Menu, PermissaoMenu, PerfilUsuario

# Register your models here.

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ordem', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ordem', 'ativo']
    ordering = ['ordem', 'nome']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['nome', 'modulo', 'url', 'menu_pai', 'ordem', 'ativo']
    list_filter = ['modulo', 'ativo', 'menu_pai']
    search_fields = ['nome', 'url', 'descricao']
    list_editable = ['ordem', 'ativo']
    ordering = ['modulo', 'ordem', 'nome']
    autocomplete_fields = ['menu_pai']


@admin.register(PermissaoMenu)
class PermissaoMenuAdmin(admin.ModelAdmin):
    list_display = ['get_identificador', 'menu', 'pode_visualizar', 'pode_criar', 'pode_editar', 'pode_excluir']
    list_filter = ['tipo', 'pode_visualizar', 'pode_criar', 'pode_editar', 'pode_excluir', 'menu__modulo']
    search_fields = ['usuario__username', 'grupo__name', 'menu__nome']
    list_editable = ['pode_visualizar', 'pode_criar', 'pode_editar', 'pode_excluir']
    autocomplete_fields = ['usuario', 'grupo', 'menu']
    
    def get_identificador(self, obj):
        if obj.tipo == 'usuario':
            return f"Usuário: {obj.usuario.username}"
        return f"Grupo: {obj.grupo.name}"
    get_identificador.short_description = 'Identificador'


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['telefone', 'celular', 'cargo', 'departamento', 'foto', 'ativo']


class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_perfil_ativo']
    
    def get_perfil_ativo(self, obj):
        try:
            return obj.perfil.ativo
        except PerfilUsuario.DoesNotExist:
            return False
    get_perfil_ativo.short_description = 'Perfil Ativo'
    get_perfil_ativo.boolean = True


# Re-registra o User com o inline do Perfil
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

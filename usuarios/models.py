from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.

class Modulo(models.Model):
    """
    Representa um módulo do sistema (ex: Financeiro, RH, TI, etc)
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name='Nome do Módulo')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    icone = models.CharField(max_length=50, blank=True, null=True, verbose_name='Ícone (classe CSS)')
    ordem = models.IntegerField(default=0, verbose_name='Ordem de Exibição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Menu(models.Model):
    """
    Representa um menu dentro de um módulo
    """
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='menus', verbose_name='Módulo')
    nome = models.CharField(max_length=100, verbose_name='Nome do Menu')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    url = models.CharField(max_length=200, verbose_name='URL')
    icone = models.CharField(max_length=50, blank=True, null=True, verbose_name='Ícone (classe CSS)')
    ordem = models.IntegerField(default=0, verbose_name='Ordem de Exibição')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    menu_pai = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, 
                                   related_name='submenus', verbose_name='Menu Pai')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['modulo', 'ordem', 'nome']
        unique_together = ['modulo', 'url']

    def __str__(self):
        if self.menu_pai:
            return f"{self.modulo.nome} > {self.menu_pai.nome} > {self.nome}"
        return f"{self.modulo.nome} > {self.nome}"


class PermissaoMenu(models.Model):
    """
    Define quais menus um usuário ou grupo tem acesso
    """
    TIPO_CHOICES = [
        ('usuario', 'Usuário'),
        ('grupo', 'Grupo'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, 
                                related_name='permissoes_menu', verbose_name='Usuário')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, 
                              related_name='permissoes_menu', verbose_name='Grupo')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='permissoes', verbose_name='Menu')
    pode_visualizar = models.BooleanField(default=True, verbose_name='Pode Visualizar')
    pode_criar = models.BooleanField(default=False, verbose_name='Pode Criar')
    pode_editar = models.BooleanField(default=False, verbose_name='Pode Editar')
    pode_excluir = models.BooleanField(default=False, verbose_name='Pode Excluir')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Permissão de Menu'
        verbose_name_plural = 'Permissões de Menus'
        unique_together = [
            ['usuario', 'menu'],
            ['grupo', 'menu']
        ]

    def __str__(self):
        if self.tipo == 'usuario':
            return f"{self.usuario.username} - {self.menu.nome}"
        return f"{self.grupo.name} - {self.menu.nome}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.tipo == 'usuario' and not self.usuario:
            raise ValidationError('Usuário é obrigatório quando o tipo for "usuário"')
        if self.tipo == 'grupo' and not self.grupo:
            raise ValidationError('Grupo é obrigatório quando o tipo for "grupo"')


class PerfilUsuario(models.Model):
    """
    Estende o modelo User com informações adicionais
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuário')
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefone')
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name='Celular')
    cargo = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cargo')
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Departamento')
    foto = models.ImageField(upload_to='usuarios/fotos/', blank=True, null=True, verbose_name='Foto')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

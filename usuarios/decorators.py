from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import PermissaoMenu, Menu


def encontrar_menu(url_menu):
    """
    Busca um menu de forma inteligente:
    1. Primeiro tenta URL exata
    2. Se não encontrar e URL não começa com /, adiciona / no início e final
    3. Se ainda não encontrar, busca pelo módulo
    """
    # Tenta URL exata primeiro
    menu = Menu.objects.filter(url=url_menu, ativo=True).first()
    if menu:
        return menu
    
    # Se não começa com /, tenta adicionar barras
    if not url_menu.startswith('/'):
        url_com_barras = f'/{url_menu}/'
        menu = Menu.objects.filter(url=url_com_barras, ativo=True).first()
        if menu:
            return menu
        
        # Tenta buscar pelo módulo (qualquer menu do módulo)
        menu = Menu.objects.filter(
            modulo__nome__iexact=url_menu,
            ativo=True,
            menu_pai__isnull=True  # Pega o menu principal (sem pai)
        ).first()
        if menu:
            return menu
    
    return None


def verificar_permissao_menu(url_menu):
    """
    Decorator para verificar se o usuário tem permissão para acessar um menu específico
    
    Uso:
    @verificar_permissao_menu('/dashboard/')
    def minha_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Você precisa estar autenticado.')
                return redirect('login')
            
            # Superusuário tem acesso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verifica se o menu existe
            menu = encontrar_menu(url_menu)
            if not menu:
                messages.error(request, 'Menu não encontrado.')
                return redirect('home_modulos')
            
            # Verifica permissão do usuário
            tem_permissao = PermissaoMenu.objects.filter(
                usuario=request.user,
                menu=menu,
                pode_visualizar=True
            ).exists()
            
            # Se não tem permissão direta, verifica permissão por grupo
            if not tem_permissao:
                grupos_usuario = request.user.groups.all()
                tem_permissao = PermissaoMenu.objects.filter(
                    grupo__in=grupos_usuario,
                    menu=menu,
                    pode_visualizar=True
                ).exists()
            
            if not tem_permissao:
                messages.error(request, 'Você não tem permissão para acessar este recurso.')
                return redirect('home_modulos')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def verificar_permissao_acao(url_menu, acao):
    """
    Decorator para verificar permissões específicas (criar, editar, excluir)
    
    Uso:
    @verificar_permissao_acao('/usuarios/', 'criar')
    def criar_usuario(request):
        ...
    
    Ações disponíveis: 'criar', 'editar', 'excluir'
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Você precisa estar autenticado.')
                return redirect('login')
            
            # Superusuário tem acesso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verifica se o menu existe
            menu = encontrar_menu(url_menu)
            if not menu:
                messages.error(request, 'Menu não encontrado.')
                return redirect('home_modulos')
            
            # Mapeia a ação para o campo do modelo
            campos_acao = {
                'criar': 'pode_criar',
                'editar': 'pode_editar',
                'excluir': 'pode_excluir'
            }
            
            if acao not in campos_acao:
                messages.error(request, 'Ação inválida.')
                return redirect('home_modulos')
            
            campo = campos_acao[acao]
            
            # Verifica permissão do usuário
            filtro = {
                'usuario': request.user,
                'menu': menu,
                campo: True
            }
            tem_permissao = PermissaoMenu.objects.filter(**filtro).exists()
            
            # Se não tem permissão direta, verifica permissão por grupo
            if not tem_permissao:
                grupos_usuario = request.user.groups.all()
                filtro['grupo__in'] = grupos_usuario
                del filtro['usuario']
                tem_permissao = PermissaoMenu.objects.filter(**filtro).exists()
            
            if not tem_permissao:
                messages.error(request, f'Você não tem permissão para {acao} neste recurso.')
                return redirect('home_modulos')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permissao_menu_required(url_menu, acao='visualizar'):
    """
    Decorator unificado para verificar permissões de menu
    
    Uso:
    @permissao_menu_required('/financeiro/', 'visualizar')
    def minha_view(request):
        ...
    
    Ações disponíveis: 'visualizar', 'criar', 'editar', 'excluir'
    Também aceita formato antigo: 'view', 'add', 'change', 'delete'
    """
    # Mapa de conversão do formato antigo para novo
    mapa_acoes = {
        'view': 'visualizar',
        'add': 'criar',
        'change': 'editar',
        'delete': 'excluir'
    }
    
    # Converte ação antiga para nova
    if acao in mapa_acoes:
        acao = mapa_acoes[acao]
    
    # Converte nome do módulo para URL se necessário
    # Se url_menu não começa com '/', assume que é um nome de módulo
    if not url_menu.startswith('/'):
        url_menu = f'/{url_menu}/'
    
    if acao == 'visualizar':
        return verificar_permissao_menu(url_menu)
    else:
        return verificar_permissao_acao(url_menu, acao)

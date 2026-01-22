from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import PermissaoMenu, Menu


def encontrar_menu(url_menu):
    """
    Busca um menu de forma inteligente:
    1. Primeiro tenta URL exata
    2. Se URL termina com / mas não é completa (ex: /cadastros/), tenta encontrar o dashboard do módulo
    3. Se não começa com /, busca pelo nome do módulo
    """
    # Tenta URL exata primeiro
    menu = Menu.objects.filter(url=url_menu, ativo=True).first()
    if menu:
        return menu
    
    # Se começa com / e termina com / mas não encontrou (ex: /cadastros/)
    # Tenta encontrar o dashboard desse módulo
    if url_menu.startswith('/') and url_menu.endswith('/'):
        # Remove as barras para pegar o nome: /cadastros/ -> cadastros
        nome_modulo = url_menu.strip('/')
        
        # Tenta encontrar menu Dashboard desse módulo
        menu = Menu.objects.filter(
            modulo__nome__iexact=nome_modulo,
            nome__iexact='dashboard',
            ativo=True
        ).first()
        if menu:
            return menu
        
        # Se não tem dashboard, pega o primeiro menu do módulo
        menu = Menu.objects.filter(
            modulo__nome__iexact=nome_modulo,
            ativo=True,
            menu_pai__isnull=True
        ).first()
        if menu:
            return menu
    
    # Se não começa com /, tenta buscar pelo nome do módulo
    if not url_menu.startswith('/'):
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
    
    # Não precisa converter mais - encontrar_menu já faz isso
    # A função encontrar_menu aceita tanto 'financeiro' quanto '/financeiro/' quanto '/financeiro/dashboard/'
    
    if acao == 'visualizar':
        return verificar_permissao_menu(url_menu)
    else:
        return verificar_permissao_acao(url_menu, acao)

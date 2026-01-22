from django import template
from usuarios.models import PermissaoMenu, Modulo, Menu

register = template.Library()


@register.simple_tag(takes_context=True)
def get_menus_usuario(context):
    """
    Retorna todos os módulos e menus que o usuário tem permissão para visualizar
    
    Uso no template:
    {% get_menus_usuario as menus %}
    {% for modulo in menus %}
        {{ modulo.nome }}
        {% for menu in modulo.menus_permitidos %}
            {{ menu.nome }}
        {% endfor %}
    {% endfor %}
    """
    request = context['request']
    user = request.user
    
    if not user.is_authenticated:
        return []
    
    # Superusuário vê tudo
    if user.is_superuser:
        modulos = Modulo.objects.filter(ativo=True).prefetch_related('menus')
        for modulo in modulos:
            modulo.menus_permitidos = modulo.menus.filter(ativo=True, menu_pai__isnull=True)
        return modulos
    
    # Busca permissões do usuário
    permissoes_usuario = PermissaoMenu.objects.filter(
        usuario=user,
        pode_visualizar=True,
        menu__ativo=True
    ).select_related('menu', 'menu__modulo')
    
    # Busca permissões dos grupos do usuário
    grupos_usuario = user.groups.all()
    permissoes_grupo = PermissaoMenu.objects.filter(
        grupo__in=grupos_usuario,
        pode_visualizar=True,
        menu__ativo=True
    ).select_related('menu', 'menu__modulo')
    
    # Combina as permissões
    menus_permitidos_ids = set()
    for perm in permissoes_usuario:
        menus_permitidos_ids.add(perm.menu.id)
    for perm in permissoes_grupo:
        menus_permitidos_ids.add(perm.menu.id)
    
    # Busca os módulos que têm menus permitidos
    menus_permitidos = Menu.objects.filter(
        id__in=menus_permitidos_ids,
        ativo=True,
        menu_pai__isnull=True
    ).select_related('modulo')
    
    # Organiza por módulo
    modulos_dict = {}
    for menu in menus_permitidos:
        if menu.modulo.ativo:
            if menu.modulo.id not in modulos_dict:
                modulos_dict[menu.modulo.id] = {
                    'modulo': menu.modulo,
                    'menus': []
                }
            modulos_dict[menu.modulo.id]['menus'].append(menu)
    
    # Prepara retorno
    modulos = []
    for mod_data in modulos_dict.values():
        modulo = mod_data['modulo']
        modulo.menus_permitidos = sorted(mod_data['menus'], key=lambda x: x.ordem)
        modulos.append(modulo)
    
    return sorted(modulos, key=lambda x: x.ordem)


@register.simple_tag(takes_context=True)
def tem_permissao_menu(context, url_menu, acao='visualizar'):
    """
    Verifica se o usuário tem permissão para uma ação específica em um menu
    
    Uso no template:
    {% tem_permissao_menu '/usuarios/' 'criar' as pode_criar %}
    {% if pode_criar %}
        <a href="{% url 'criar_usuario' %}">Criar Usuário</a>
    {% endif %}
    
    Ações: visualizar, criar, editar, excluir
    """
    request = context['request']
    user = request.user
    
    if not user.is_authenticated:
        return False
    
    # Superusuário tem todas as permissões
    if user.is_superuser:
        return True
    
    # Verifica se o menu existe usando encontrar_menu
    from usuarios.decorators import encontrar_menu
    menu = encontrar_menu(url_menu)
    if not menu:
        return False
    
    # Mapeia ação para campo
    campos_acao = {
        'visualizar': 'pode_visualizar',
        'criar': 'pode_criar',
        'editar': 'pode_editar',
        'excluir': 'pode_excluir'
    }
    
    if acao not in campos_acao:
        return False
    
    campo = campos_acao[acao]
    
    # Verifica permissão do usuário
    filtro = {
        'usuario': user,
        'menu': menu,
        campo: True
    }
    if PermissaoMenu.objects.filter(**filtro).exists():
        return True
    
    # Verifica permissão dos grupos
    grupos_usuario = user.groups.all()
    filtro['grupo__in'] = grupos_usuario
    del filtro['usuario']
    return PermissaoMenu.objects.filter(**filtro).exists()


@register.simple_tag(takes_context=True)
def get_submenus(context, menu_pai):
    """
    Retorna os submenus de um menu pai que o usuário tem permissão
    
    Uso no template:
    {% get_submenus menu as submenus %}
    {% for submenu in submenus %}
        {{ submenu.nome }}
    {% endfor %}
    """
    request = context['request']
    user = request.user
    
    if not user.is_authenticated:
        return []
    
    submenus = Menu.objects.filter(
        menu_pai=menu_pai,
        ativo=True
    ).order_by('ordem')
    
    # Superusuário vê tudo
    if user.is_superuser:
        return submenus
    
    # Filtra submenus com permissão
    submenus_permitidos = []
    for submenu in submenus:
        # Verifica permissão do usuário
        if PermissaoMenu.objects.filter(
            usuario=user,
            menu=submenu,
            pode_visualizar=True
        ).exists():
            submenus_permitidos.append(submenu)
            continue
        
        # Verifica permissão dos grupos
        grupos_usuario = user.groups.all()
        if PermissaoMenu.objects.filter(
            grupo__in=grupos_usuario,
            menu=submenu,
            pode_visualizar=True
        ).exists():
            submenus_permitidos.append(submenu)
    
    return submenus_permitidos


@register.filter
def get_item(mapping, key):
    """Retorna mapping[key] ou None se não existir."""
    try:
        return mapping.get(key)
    except Exception:
        return None

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group
from django.db.models import Q
from .models import PerfilUsuario, PermissaoMenu, Modulo, Menu
from .decorators import verificar_permissao_menu, verificar_permissao_acao

# Create your views here.


@login_required
def modulos(request):
    """Landing page com os módulos disponíveis conforme permissões."""
    user = request.user

    def build_modulo_entry(modulo, menus):
        menus_list = list(menus)
        if not menus_list:
            return None
        primary_url = menus_list[0].url
        primary_label = "Acessar"
        nome_normalizado = modulo.nome.lower().strip()

        if nome_normalizado == 'sistema':
            alvo = next((m for m in menus_list if m.url == '/usuarios/' or m.nome.lower().startswith('usu')), menus_list[0])
            primary_url = alvo.url
            primary_label = "Gestão de Acessos"
        return {
            'modulo': modulo,
            'menus': menus_list,
            'primary_url': primary_url,
            'primary_label': primary_label,
        }

    # Superusuário enxerga todos os módulos com menus ativos
    if user.is_superuser:
        modulos_qs = Modulo.objects.filter(ativo=True).prefetch_related('menus')
        modulos_permitidos = []
        for modulo in modulos_qs:
            menus_modulo = modulo.menus.filter(ativo=True, menu_pai__isnull=True).order_by('ordem', 'nome')
            entry = build_modulo_entry(modulo, menus_modulo)
            if entry:
                modulos_permitidos.append(entry)
        context = {
            'modulos': modulos_permitidos,
            'hide_sidebar': True,
        }
        return render(request, 'usuarios/modulos.html', context)

    # Permissões por usuário e grupos
    permissoes_usuario = PermissaoMenu.objects.filter(
        usuario=user,
        pode_visualizar=True,
        menu__ativo=True
    ).select_related('menu', 'menu__modulo')

    grupos_usuario = user.groups.all()
    permissoes_grupo = PermissaoMenu.objects.filter(
        grupo__in=grupos_usuario,
        pode_visualizar=True,
        menu__ativo=True
    ).select_related('menu', 'menu__modulo')

    menu_ids = {p.menu.id for p in permissoes_usuario} | {p.menu.id for p in permissoes_grupo}

    menus_permitidos = Menu.objects.filter(
        id__in=menu_ids,
        ativo=True,
        menu_pai__isnull=True
    ).select_related('modulo').order_by('modulo__ordem', 'ordem', 'nome')

    modulos_dict = {}
    for menu in menus_permitidos:
        modulo = menu.modulo
        if not modulo.ativo:
            continue
        if modulo.id not in modulos_dict:
            modulos_dict[modulo.id] = {
                'modulo': modulo,
                'menus': [],
            }
        modulos_dict[modulo.id]['menus'].append(menu)

    modulos_list = []
    for data in modulos_dict.values():
        entry = build_modulo_entry(data['modulo'], data['menus'])
        if entry:
            modulos_list.append(entry)

    context = {
        'modulos': modulos_list,
        'hide_sidebar': True,
    }
    return render(request, 'usuarios/modulos.html', context)


def logout_custom(request):
    """Logout via GET e redireciona para a tela de login."""
    logout(request)
    return redirect('/accounts/login/')

@login_required
def dashboard(request):
    """
    Dashboard principal - exibe informações gerais
    """
    context = {
        'total_usuarios': User.objects.filter(is_active=True).count(),
        'total_modulos': Modulo.objects.filter(ativo=True).count(),
        'total_menus': Menu.objects.filter(ativo=True).count(),
    }
    return render(request, 'usuarios/dashboard.html', context)


@login_required
@verificar_permissao_menu('/usuarios/')
def listar_usuarios(request):
    """
    Lista todos os usuários do sistema
    """
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'username').strip() or 'username'

    # Whitelist de ordenação para evitar SQL injection
    allowed_sorts = {
        'username': 'username',
        '-username': '-username',
        'nome': 'first_name',
        '-nome': '-first_name',
        'sobrenome': 'last_name',
        '-sobrenome': '-last_name',
        'email': 'email',
        '-email': '-email',
        'cargo': 'perfil__cargo',
        '-cargo': '-perfil__cargo',
        'departamento': 'perfil__departamento',
        '-departamento': '-perfil__departamento',
        'status': 'is_active',
        '-status': '-is_active',
    }
    order_field = allowed_sorts.get(sort, 'username')

    usuarios = User.objects.select_related('perfil').all()

    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(perfil__cargo__icontains=q)
            | Q(perfil__departamento__icontains=q)
        )

    usuarios = usuarios.order_by(order_field)
    context = {
        'usuarios': usuarios,
        'hide_sidebar': True,
        'q': q,
        'sort': sort,
    }
    return render(request, 'usuarios/listar_usuarios.html', context)


@login_required
@verificar_permissao_acao('/usuarios/', 'criar')
def criar_usuario(request):
    """
    Cria um novo usuário
    """
    if request.method == 'POST':
        # Processa o formulário
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        try:
            # Cria o usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Cria o perfil
            PerfilUsuario.objects.create(
                usuario=user,
                telefone=request.POST.get('telefone', ''),
                celular=request.POST.get('celular', ''),
                cargo=request.POST.get('cargo', ''),
                departamento=request.POST.get('departamento', '')
            )
            
            messages.success(request, f'Usuário {username} criado com sucesso!')
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {str(e)}')
    
    context = {
        'grupos': Group.objects.all()
    }
    context['hide_sidebar'] = True
    return render(request, 'usuarios/criar_usuario.html', context)


@login_required
@verificar_permissao_acao('/usuarios/', 'editar')
def editar_usuario(request, user_id):
    """
    Edita um usuário existente
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            user.username = request.POST.get('username', user.username)
            user.email = request.POST.get('email', user.email)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.is_active = request.POST.get('is_active') == 'on'
            user.save()
            
            # Atualiza o perfil
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            perfil.telefone = request.POST.get('telefone', '')
            perfil.celular = request.POST.get('celular', '')
            perfil.cargo = request.POST.get('cargo', '')
            perfil.departamento = request.POST.get('departamento', '')
            perfil.save()
            
            messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar usuário: {str(e)}')
    
    context = {
        'usuario': user,
        'grupos': Group.objects.all(),
        'hide_sidebar': True,
    }
    return render(request, 'usuarios/editar_usuario.html', context)


@login_required
@verificar_permissao_acao('/usuarios/', 'editar')
def alternar_status_usuario(request, user_id):
    """Ativa ou inativa um usuário e retorna à lista."""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "ativado" if user.is_active else "inativado"
    messages.success(request, f"Usuário {user.username} {status} com sucesso.")
    return redirect('listar_usuarios')


@login_required
@verificar_permissao_menu('/permissoes/')
def gerenciar_permissoes(request, user_id):
    """
    Gerencia as permissões de um usuário
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Remove permissões antigas do usuário
        PermissaoMenu.objects.filter(usuario=user).delete()
        
        # Cria novas permissões baseadas no formulário
        menus_selecionados = request.POST.getlist('menus')
        for menu_id in menus_selecionados:
            menu = Menu.objects.get(id=menu_id)
            PermissaoMenu.objects.create(
                tipo='usuario',
                usuario=user,
                menu=menu,
                pode_visualizar=True,
                pode_criar=f'criar_{menu_id}' in request.POST,
                pode_editar=f'editar_{menu_id}' in request.POST,
                pode_excluir=f'excluir_{menu_id}' in request.POST
            )
        
        messages.success(request, f'Permissões de {user.username} atualizadas com sucesso!')
        return redirect('listar_usuarios')
    
    # Busca permissões atuais do usuário
    permissoes_atuais = PermissaoMenu.objects.filter(usuario=user).select_related('menu')
    menus_com_permissao = {p.menu.id: p for p in permissoes_atuais}
    
    # Busca todos os módulos e menus
    modulos = Modulo.objects.filter(ativo=True).prefetch_related('menus')
    
    context = {
        'usuario': user,
        'modulos': modulos,
        'menus_com_permissao': menus_com_permissao,
        'hide_sidebar': True,
    }
    return render(request, 'usuarios/gerenciar_permissoes.html', context)

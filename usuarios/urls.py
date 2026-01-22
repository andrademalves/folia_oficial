from django.urls import path
from . import views

urlpatterns = [
    path('', views.modulos, name='home_modulos'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/criar/', views.criar_usuario, name='criar_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/ativar-desativar/', views.alternar_status_usuario, name='alternar_status_usuario'),
    path('usuarios/<int:user_id>/permissoes/', views.gerenciar_permissoes, name='gerenciar_permissoes'),
]

from django.urls import path
from . import views

app_name = 'importacoes'

urlpatterns = [
    path('', views.dashboard_importacoes, name='dashboard'),
    path('dashboard/', views.dashboard_importacoes, name='dashboard_importacoes'),
    path('cadastro-geral/', views.importar_cadastro_geral, name='cadastro_geral'),
    path('notas-fiscais/', views.importar_notas_fiscais, name='notas_fiscais'),
    path('parcelas/', views.importar_parcelas, name='parcelas'),
    path('logs/', views.logs_importacao, name='logs'),
    path('logs/<int:pk>/', views.detalhe_log, name='detalhe_log'),
    path('configurar/', views.configurar_firebird, name='configurar'),
    path('configurar-firebird/', views.configurar_firebird, name='configurar_firebird'),
    path('testar-conexao/', views.testar_conexao_firebird, name='testar_conexao'),
    # APIs
    path('api/iniciar/', views.api_iniciar_importacao, name='api_iniciar'),
    path('api/status/<int:pk>/', views.api_status_importacao, name='api_status'),
]

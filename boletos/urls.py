from django.urls import path
from . import views

app_name = 'boletos'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_boletos, name='dashboard_boletos'),
    
    # Boletos
    path('boletos/', views.lista_boletos, name='lista_boletos'),
    path('boletos/selecionar/', views.selecionar_parcelas_boleto, name='selecionar_parcelas_boleto'),
    path('boletos/gerar-lote/', views.gerar_boletos_lote, name='gerar_boletos_lote'),
    path('boletos/<int:boleto_id>/', views.detalhe_boleto, name='detalhe_boleto'),
    path('boletos/<int:boleto_id>/imprimir/', views.imprimir_boleto, name='imprimir_boleto'),
    path('boletos/<int:boleto_id>/cancelar/', views.cancelar_boleto, name='cancelar_boleto'),
    path('boletos/gerar/<int:parcela_id>/', views.gerar_boleto_parcela, name='gerar_boleto_parcela'),
    
    # Remessas CNAB
    path('remessas/', views.lista_remessas, name='lista_remessas'),
    path('remessas/gerar/', views.gerar_remessa_cnab, name='gerar_remessa_cnab'),
    path('remessas/<int:remessa_id>/', views.detalhe_remessa, name='detalhe_remessa'),
    path('remessas/<int:remessa_id>/download/', views.download_remessa, name='download_remessa'),
    
    # Configurações Bancárias
    path('configuracoes/', views.lista_configuracoes, name='lista_configuracoes'),
    path('configuracoes/criar/', views.criar_configuracao, name='criar_configuracao'),
    path('configuracoes/<int:id>/editar/', views.editar_configuracao, name='editar_configuracao'),
    path('configuracoes/<int:id>/excluir/', views.excluir_configuracao, name='excluir_configuracao'),
]

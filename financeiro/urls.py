from django.urls import path
from . import views
from . import views_conta_corrente

app_name = 'financeiro'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_financeiro, name='dashboard'),
    path('dashboard/', views.dashboard_financeiro, name='dashboard_financeiro'),
    
    # Contas a Pagar
    path('contas-pagar/', views.contaspagar_list, name='contaspagar_list'),
    path('contas-pagar/criar/', views.contaspagar_create, name='contaspagar_create'),
    path('contas-pagar/<int:pk>/editar/', views.contaspagar_edit, name='contaspagar_edit'),
    path('contas-pagar/<int:pk>/deletar/', views.contaspagar_delete, name='contaspagar_delete'),
    path('contas-pagar/<int:pk>/pagar/', views.contaspagar_pagar, name='contaspagar_pagar'),
    path('contas-pagar/<int:pk>/desmarcar-pago/', views.contaspagar_desmarcar_pago, name='contaspagar_desmarcar_pago'),
    
    # Dar Baixa
    path('dar-baixa/', views.dar_baixa, name='dar_baixa'),
    path('dar-baixa/<int:pk>/', views.dar_baixa_conta, name='dar_baixa_conta'),
    
    # Conta Corrente
    path('conta-corrente/', views_conta_corrente.conta_corrente_list, name='conta_corrente_list'),
    path('conta-corrente/<int:conta_id>/extrato/', views_conta_corrente.extrato_conta, name='extrato_conta'),
    path('movimentacao/criar/', views_conta_corrente.movimentacao_create, name='movimentacao_create'),
    path('movimentacao/<int:pk>/editar/', views_conta_corrente.movimentacao_edit, name='movimentacao_edit'),
    path('movimentacao/<int:pk>/deletar/', views_conta_corrente.movimentacao_delete, name='movimentacao_delete'),
    
    # AJAX
    path('ajax/get-subcontas/<int:conta_pai_id>/', views.get_subcontas, name='get_subcontas'),
    path('ajax/grafico-despesas/', views.grafico_despesas_por_conta, name='grafico_despesas'),
    
    # Relatórios
    path('relatorios/', views.relatorios_financeiros, name='relatorios'),
    path('relatorios/exportar-excel/', views.exportar_relatorio_excel, name='exportar_relatorio_excel'),
    path('relatorios/gerar-pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
]

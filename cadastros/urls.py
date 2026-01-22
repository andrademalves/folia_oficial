from django.urls import path
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('', views.dashboard_cadastros, name='dashboard'),
    path('dashboard/', views.dashboard_cadastros, name='dashboard_cadastros'),
    path('plano-contas/', views.plano_contas, name='plano_contas'),
    path('plano-contas/editar/<int:pk>/', views.editar_plano_conta, name='editar_plano_conta'),
    path('plano-contas/inativar/<int:pk>/', views.inativar_plano_conta, name='inativar_plano_conta'),
    path('plano-contas/ativar/<int:pk>/', views.ativar_plano_conta, name='ativar_plano_conta'),
    path('contas-financeiras/', views.contas_financeiras, name='contas_financeiras'),
    path('contas-financeiras/editar/<int:pk>/', views.editar_conta_financeira, name='editar_conta_financeira'),
    path('contas-financeiras/inativar/<int:pk>/', views.inativar_conta_financeira, name='inativar_conta_financeira'),
    path('contas-financeiras/ativar/<int:pk>/', views.ativar_conta_financeira, name='ativar_conta_financeira'),
    path('metodos-pagamento/', views.metodos_pagamento, name='metodos_pagamento'),
    path('metodos-pagamento/editar/<int:pk>/', views.editar_metodo_pagamento, name='editar_metodo_pagamento'),
    path('metodos-pagamento/inativar/<int:pk>/', views.inativar_metodo_pagamento, name='inativar_metodo_pagamento'),
    path('metodos-pagamento/ativar/<int:pk>/', views.ativar_metodo_pagamento, name='ativar_metodo_pagamento'),
    path('relatorios/', views.relatorios_cadastros, name='relatorios'),
    path('relatorios/plano-contas-pdf/', views.relatorio_plano_contas_pdf, name='relatorio_plano_contas_pdf'),
    path('relatorios/contas-ativas-pdf/', views.relatorio_contas_ativas_pdf, name='relatorio_contas_ativas_pdf'),
    path('relatorios/contas-inativas-pdf/', views.relatorio_contas_inativas_pdf, name='relatorio_contas_inativas_pdf'),
    path('relatorios/hierarquia-completa-pdf/', views.relatorio_hierarquia_completa_pdf, name='relatorio_hierarquia_completa_pdf'),
    path('relatorios/contas-bancarias-pdf/', views.relatorio_contas_bancarias_pdf, name='relatorio_contas_bancarias_pdf'),
    path('relatorios/consolidado-pdf/', views.relatorio_consolidado_pdf, name='relatorio_consolidado_pdf'),
    path('relatorios/metodos-pagamento-pdf/', views.relatorio_metodos_pagamento_pdf, name='relatorio_metodos_pagamento_pdf'),
]

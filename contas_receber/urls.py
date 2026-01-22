from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard_contas_receber'),
    
    # Notas Fiscais
    path('notas-fiscais/', views.lista_notas_fiscais, name='lista_notas_fiscais'),
    path('registrar-parcelas/', views.registrar_parcelas, name='registrar_parcelas'),
    
    # Parcelas
    path('parcelas/', views.lista_parcelas, name='lista_parcelas'),
    path('parcelas/vencimento/', views.parcelas_por_vencimento, name='parcelas_por_vencimento'),
    path('parcelas/baixa/', views.lista_parcelas_baixa, name='lista_parcelas_baixa'),
    path('parcelas/<int:parcela_id>/baixa/', views.dar_baixa_parcela, name='dar_baixa_parcela'),
    
    # Negociações
    path('negociacoes/', views.lista_historico_negociacoes, name='lista_historico_negociacoes'),
    path('negociacoes/<int:parcela_id>/processar/', views.processar_negociacao, name='processar_negociacao'),
    path('negociacoes/pdf/', views.gerar_pdf_negociacoes, name='gerar_pdf_negociacoes'),
    path('negociacoes/<int:negociacao_id>/acordo-pdf/', views.gerar_pdf_negociacao_individual, name='gerar_pdf_negociacao_individual'),
    path('verificar-parcelas-cliente/<int:cliente_id>/', views.verificar_parcelas_cliente, name='verificar_parcelas_cliente'),
    
    # Créditos
    path('creditos/', views.lista_creditos, name='lista_creditos'),
    path('creditos/criar/', views.criar_credito, name='criar_credito'),
    path('creditos/relatorio/', views.relatorio_creditos, name='relatorio_creditos'),
    path('creditos/api/nota/<int:nota_id>/', views.api_dados_nota, name='api_dados_nota'),
    path('creditos/<int:credito_id>/aprovar/', views.aprovar_credito, name='aprovar_credito'),
    path('creditos/<int:credito_id>/rejeitar/', views.rejeitar_credito, name='rejeitar_credito'),
    path('creditos/<int:credito_id>/aplicar/', views.aplicar_credito, name='aplicar_credito'),
    path('creditos/<int:credito_id>/excluir/', views.excluir_credito, name='excluir_credito'),
    
    # Aprovações (módulo separado)
    path('aprovacoes/', views.aprovacoes_creditos, name='aprovacoes_creditos'),
    path('aprovacoes/<int:credito_id>/', views.detalhe_credito_aprovacao, name='detalhe_credito_aprovacao'),
    
    # Origens
    path('origens/', views.lista_origens, name='lista_origens'),
    path('origens/criar/', views.criar_origem, name='criar_origem'),
    path('origens/<int:origem_id>/editar/', views.editar_origem, name='editar_origem'),
    path('origens/<int:origem_id>/excluir/', views.excluir_origem, name='excluir_origem'),
    
    # Exportações
    path('exportar/excel/', views.exportar_parcelas_excel, name='exportar_parcelas_excel'),
    path('exportar/pdf/', views.exportar_parcelas_pdf, name='exportar_parcelas_pdf'),
    
    # Relatórios PDF
    path('relatorios/', views.menu_relatorios, name='menu_relatorios'),
    path('relatorios/titulos-vencer/pdf/', views.relatorio_titulos_vencer_pdf, name='relatorio_titulos_vencer_pdf'),
    path('relatorios/inadimplencia/pdf/', views.relatorio_titulos_vencidos_pdf, name='relatorio_titulos_vencidos_pdf'),
    path('relatorios/recebimentos/pdf/', views.relatorio_recebimentos_pdf, name='relatorio_recebimentos_pdf'),
    path('relatorios/fluxo-caixa/pdf/', views.relatorio_fluxo_caixa_pdf, name='relatorio_fluxo_caixa_pdf'),
    path('relatorios/cliente/<int:cliente_id>/pdf/', views.relatorio_por_cliente_pdf, name='relatorio_por_cliente_pdf'),
    
    # Relatórios Excel
    path('relatorios/titulos-vencer/excel/', views.relatorio_titulos_vencer_excel, name='relatorio_titulos_vencer_excel'),
    path('relatorios/inadimplencia/excel/', views.relatorio_titulos_vencidos_excel, name='relatorio_titulos_vencidos_excel'),
    path('relatorios/recebimentos/excel/', views.relatorio_recebimentos_excel, name='relatorio_recebimentos_excel'),
    path('relatorios/fluxo-caixa/excel/', views.relatorio_fluxo_caixa_excel, name='relatorio_fluxo_caixa_excel'),
    path('relatorios/cliente/<int:cliente_id>/excel/', views.relatorio_por_cliente_excel, name='relatorio_por_cliente_excel'),
    
    # Extrato por Período (PDF e Excel)
    path('relatorios/extrato-periodo/pdf/', views.relatorio_extrato_periodo_pdf, name='relatorio_extrato_periodo_pdf'),
    path('relatorios/extrato-periodo/excel/', views.relatorio_extrato_periodo_excel, name='relatorio_extrato_periodo_excel'),
]

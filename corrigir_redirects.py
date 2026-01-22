import re

filepath = r'c:\HD_Antigo\01- Projetos Dev\1.3 Gestao\boletos\views.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de URLs do boletos que precisam do namespace
urls_boletos = [
    'dashboard_boletos', 'lista_boletos', 'selecionar_parcelas_boleto',
    'gerar_boletos_lote', 'detalhe_boleto', 'imprimir_boleto', 
    'cancelar_boleto', 'gerar_boleto_parcela', 'lista_remessas',
    'gerar_remessa_cnab', 'detalhe_remessa', 'download_remessa',
    'lista_configuracoes', 'criar_configuracao', 'editar_configuracao',
    'excluir_configuracao'
]

original = content
for url in urls_boletos:
    # Padrão: redirect('url', ...
    pattern = f"redirect('{url}'"
    replacement = f"redirect('boletos:{url}'"
    content = content.replace(pattern, replacement)

if content != original:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('✓ Todos os redirects corrigidos!')
else:
    print('Nenhuma mudança necessária')

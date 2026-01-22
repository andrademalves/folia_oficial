import os
import re

# Lista de templates e as URLs que precisam do namespace
templates_dir = r'c:\HD_Antigo\01- Projetos Dev\1.3 Gestao\boletos\templates\boletos'

# URLs que precisam do namespace boletos:
urls_boletos = [
    'dashboard_boletos',
    'lista_boletos',
    'selecionar_parcelas_boleto',
    'gerar_boletos_lote',
    'detalhe_boleto',
    'imprimir_boleto',
    'cancelar_boleto',
    'gerar_boleto_parcela',
    'lista_remessas',
    'gerar_remessa_cnab',
    'detalhe_remessa',
    'download_remessa',
    'lista_configuracoes',
    'criar_configuracao',
    'editar_configuracao',
    'excluir_configuracao',
]

# Processar todos os arquivos HTML
for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(templates_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Substituir cada URL
        for url_name in urls_boletos:
            # Padrão: {% url 'nome_url' %} ou {% url 'nome_url' parametro %}
            # Substituir por: {% url 'boletos:nome_url' %} ou {% url 'boletos:nome_url' parametro %}
            
            # Sem parâmetros
            pattern1 = f"{{% url '{url_name}' %}}"
            replacement1 = f"{{% url 'boletos:{url_name}' %}}"
            content = content.replace(pattern1, replacement1)
            
            # Com parâmetros (qualquer coisa após o nome da URL)
            pattern2 = re.compile(f"{{% url '{url_name}' ([^%]+)%}}")
            replacement2 = f"{{% url 'boletos:{url_name}' \\1%}}"
            content = pattern2.sub(replacement2, content)
        
        # Salvar se houve mudanças
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ Atualizado: {filename}')
        else:
            print(f'  Sem mudanças: {filename}')

print('\n✓ Namespaces corrigidos com sucesso!')

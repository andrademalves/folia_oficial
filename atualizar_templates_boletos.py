"""
Script para atualizar todos os templates do módulo boletos
para usar a sidebar e estilos padronizados
"""
import os
import re

# Templates a atualizar
templates = [
    'lista_boletos.html',
    'lista_remessas.html',
    'lista_configuracoes.html',
    'selecionar_parcelas.html',
    'gerar_remessa.html',
    'detalhe_remessa.html',
    'detalhe_boleto.html',
    'form_configuracao.html',
]

base_path = r'c:\HD_Antigo\01- Projetos Dev\1.3 Gestao\boletos\templates\boletos'

sidebar_pattern = r'<div class="sidebar">.*?</div>\s*</div>\s*<div class="col-md-10">'

sidebar_replacement = '''{% include 'boletos/includes/sidebar.html' %}
    </div>
    <div class="col-md-10">'''

for template in templates:
    file_path = os.path.join(base_path, template)
    
    if not os.path.exists(file_path):
        print(f"⏭️  Ignorando {template} (não encontrado)")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir sidebar
    original_len = len(content)
    content_new = re.sub(sidebar_pattern, sidebar_replacement, content, flags=re.DOTALL)
    
    if len(content_new) != original_len:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_new)
        print(f"✅ Atualizado: {template}")
    else:
        print(f"⚠️  Não modificado: {template} (padrão não encontrado)")

print("\n✅ Atualização concluída!")

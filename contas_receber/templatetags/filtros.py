from django import template

register = template.Library()

@register.filter
def formato_brasileiro(valor):
    """Formata número para padrão brasileiro"""
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return valor

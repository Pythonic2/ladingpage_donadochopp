from django import template

register = template.Library()

@register.filter
def reais(value):
    try:
        return "R$ {:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value
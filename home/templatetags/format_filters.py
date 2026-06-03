from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def reais(value):
    try:
        return "R$ {:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return value


@register.filter
def add_value(value, amount):
    try:
        return float(value) + float(amount)
    except:
        return value


@register.filter
def cores_admin(value):
    if value is None:
        return ""

    color_classes = {
        "verde": "text-leaf",
        "vermelho": "text-flame",
        "amarelo": "text-beer",
        "marrom": "text-ink",
        "branco": "text-white",
    }
    text = conditional_escape(str(value))

    for tag, css_class in color_classes.items():
        pattern = re.compile(rf"&lt;{tag}&gt;(.*?)&lt;/{tag}&gt;", re.IGNORECASE | re.DOTALL)
        text = pattern.sub(rf'<span class="{css_class}">\1</span>', text)

    return mark_safe(text)


@register.filter
def destacar_titulo(value, secao):
    if value is None:
        return ""

    legacy_colors = {
        "verde": "#169b4f",
        "vermelho": "#df2f24",
        "amarelo": "#ffc247",
        "marrom": "#20130f",
        "branco": "#ffffff",
    }
    text = conditional_escape(str(value))
    phrase = getattr(secao, "titulo_destaque", "") or ""
    if not phrase:
        return mark_safe(text)

    escaped_phrase = conditional_escape(phrase)
    color = str(getattr(secao, "cor_titulo_destaque", "") or "#169b4f").strip()
    color = legacy_colors.get(color, color)
    safe_color_patterns = (
        r"#[0-9a-fA-F]{3,8}",
        r"rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)",
        r"rgba\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*(0|1|0?\.\d+)\s*\)",
        r"hsl\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*\)",
        r"hsla\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*,\s*(0|1|0?\.\d+)\s*\)",
    )
    if not any(re.fullmatch(pattern, color) for pattern in safe_color_patterns):
        color = "#169b4f"
    pattern = re.compile(re.escape(str(escaped_phrase)), re.IGNORECASE)
    highlighted = pattern.sub(
        lambda match: f'<span style="color: {color};">{match.group(0)}</span>',
        text,
        count=1,
    )
    return mark_safe(highlighted)


@register.filter
def titulo_hero_formatado(value, secao):
    if value is None:
        return ""

    raw_text = str(value)
    if ":" not in raw_text:
        return destacar_titulo(raw_text, secao)

    antes, depois = raw_text.split(":", 1)
    primeira_linha = conditional_escape(f"{antes.strip()}:")
    segunda_linha = destacar_titulo(depois.strip(), secao)

    return mark_safe(
        '<span class="block text-[0.72em] leading-[1.04] lg:text-[0.62em]">'
        f"{primeira_linha}"
        "</span>"
        '<span class="mt-1 block leading-[.96]">'
        f"{segunda_linha}"
        "</span>"
    )

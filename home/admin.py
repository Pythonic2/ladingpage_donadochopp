from django.contrib import admin
from django import forms
from .models import (
    Produto,
    Pedido,
    Transacao,
    Pergunta,
    Evento,
    Depoimento,
    ConfiguracaoLanding,
    MidiaLanding,
    SecaoLanding,
    SecaoLandingMidia,
    SecaoLandingCard,
    SecaoLandingLinhaTabela,
    BlocoFixoLanding,
)

# Register your models here.
admin.site.register(Pedido)
admin.site.register(Transacao)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "preco_sem_desconto", "estoque", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    search_fields = ("nome", "descricao", "slug")


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "ordem", "ativo", "criado_em")
    list_editable = ("ordem", "ativo")
    list_filter = ("ativo", "criado_em")
    search_fields = ("titulo", "categoria", "descricao")


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ("nome_cliente", "tipo_midia", "contexto", "ordem", "ativo", "criado_em")
    list_editable = ("ordem", "ativo")
    list_filter = ("tipo_midia", "ativo", "criado_em")
    search_fields = ("nome_cliente", "contexto", "texto")


@admin.register(ConfiguracaoLanding)
class ConfiguracaoLandingAdmin(admin.ModelAdmin):
    list_display = ("url_publica_site", "mostrar_barra_topo", "texto_barra_topo", "modo_black_friday", "texto_selo_black", "atualizado_em")
    fields = ("url_publica_site", "mostrar_barra_topo", "texto_barra_topo", "modo_black_friday", "texto_selo_black", "atualizado_em")
    readonly_fields = ("atualizado_em",)

    def has_add_permission(self, request):
        return not ConfiguracaoLanding.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MidiaLanding)
class MidiaLandingAdmin(admin.ModelAdmin):
    list_display = ("titulo", "chave", "tipo", "uso_no_html", "ordem", "ativo", "criado_em")
    list_editable = ("ordem", "ativo")
    list_filter = ("chave", "tipo", "ativo", "criado_em")
    ordering = ("ordem", "chave", "-criado_em")
    search_fields = ("titulo", "descricao", "link")
    readonly_fields = ("uso_no_html",)

    fieldsets = (
        (
            "Arquivo",
            {
                "fields": (
                    "ativo",
                    "chave",
                    "uso_no_html",
                    "tipo",
                    "arquivo",
                    "titulo",
                    "descricao",
                    "link",
                    "ordem",
                )
            },
        ),
    )

    @admin.display(description="Onde aparece")
    def uso_no_html(self, obj):
        usos = {
            "hero_principal": "Imagem grande do hero no desktop.",
            "lucro_operacao": "Imagem da seção de lucro, caso a seção não tenha imagem própria.",
            "video_thumb": "Capa do vídeo principal.",
            "video_principal": "Arquivo do vídeo principal.",
            "prova_social": "Cards da seção Prova social.",
            "galeria": "Imagens da seção Galeria.",
            "logo_header": "Logo usada no cabeçalho.",
            "logo_footer": "Logo pequena do rodapé.",
        }
        return usos.get(obj.chave, "Mídia cadastrada, mas sem uso específico no template.")


class SecaoLandingCardInline(admin.TabularInline):
    model = SecaoLandingCard
    extra = 1
    fields = ("titulo", "valor", "descricao", "ordem", "ativo")


class SecaoLandingLinhaTabelaInline(admin.TabularInline):
    model = SecaoLandingLinhaTabela
    extra = 1
    fields = ("rotulo", "valor", "destacar", "ordem", "ativo")


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleFileField, self).clean(file, initial) for file in files]


class SecaoLandingAdminForm(forms.ModelForm):
    cor_titulo_destaque = forms.CharField(
        required=False,
        label="Cor da frase destacada",
        help_text="Você pode digitar #169b4f, rgb(22,155,79), rgba(...) ou hsl(...). O seletor ao lado preenche em hexadecimal.",
        widget=forms.TextInput(
            attrs={
                "class": "vTextField color-css-input",
                "placeholder": "#169b4f ou rgb(22,155,79)",
            }
        ),
    )
    arquivos_multiplos = MultipleFileField(
        required=False,
        label="Adicionar várias imagens",
        help_text="Você pode adicionar uma série de imagens em qualquer seção. Elas aparecem como carrossel compacto no site.",
    )

    class Meta:
        model = SecaoLanding
        fields = "__all__"

    class Media:
        js = ("admin/js/secao_landing_color_picker.js",)

class SecaoLandingMidiaInline(admin.TabularInline):
    model = SecaoLandingMidia
    extra = 1
    fields = ("arquivo", "tipo", "papel", "titulo", "descricao", "link", "ordem", "ativo")


@admin.register(SecaoLanding)
class SecaoLandingAdmin(admin.ModelAdmin):
    form = SecaoLandingAdminForm
    list_display = ("titulo", "tipo", "fundo", "cor_titulo", "ordem", "ativo", "criado_em")
    list_editable = ("ordem", "ativo")
    list_filter = ("tipo", "fundo", "cor_titulo", "ativo", "criado_em")
    search_fields = ("titulo", "etiqueta", "descricao", "slug", "ancora")
    prepopulated_fields = {"slug": ("titulo",)}
    inlines = (SecaoLandingMidiaInline, SecaoLandingCardInline, SecaoLandingLinhaTabelaInline)
    fieldsets = (
        (
            "Identificação",
            {
                "fields": (
                    "ativo",
                    "ordem",
                    "tipo",
                    "slug",
                    "ancora",
                    "arquivos_multiplos",
                )
            },
        ),
        (
            "Textos principais",
            {
                "fields": (
                    "etiqueta",
                    "titulo",
                    "titulo_destaque",
                    "cor_titulo_destaque",
                    "descricao",
                    "texto_final",
                    "observacao",
                )
            },
        ),
        (
            "Imagem e tabela",
            {
                "fields": (
                    "imagem",
                    "imagem_titulo",
                    "cabecalho_tabela_esquerda",
                    "cabecalho_tabela_direita",
                )
            },
        ),
        (
            "Destaque do painel",
            {
                "fields": (
                    "destaque_etiqueta",
                    "destaque_valor",
                    "destaque_descricao",
                    "destaque_observacao",
                )
            },
        ),
        (
            "Cores",
            {
                "fields": (
                    "fundo",
                    "cor_titulo",
                )
            },
        ),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        arquivos = form.cleaned_data.get("arquivos_multiplos") or []
        if not arquivos:
            return
        start_order = form.instance.midias.count()
        for index, arquivo in enumerate(arquivos, start=start_order):
            SecaoLandingMidia.objects.create(
                secao=form.instance,
                arquivo=arquivo,
                tipo="imagem",
                papel="item",
                titulo=getattr(arquivo, "name", ""),
                ordem=index,
                ativo=True,
            )


@admin.register(BlocoFixoLanding)
class BlocoFixoLandingAdmin(admin.ModelAdmin):
    list_display = ("chave", "nome", "ordem", "ativo", "atualizado_em")
    list_editable = ("ordem", "ativo")
    list_filter = ("ativo",)
    ordering = ("ordem", "chave")

    @admin.display(description="Seção")
    def nome(self, obj):
        return obj.get_chave_display()


admin.site.unregister(MidiaLanding)
admin.site.unregister(BlocoFixoLanding)


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("nome", "whatsapp", "respondida", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("nome", "whatsapp", "mensagem", "resposta")
    readonly_fields = ("nome", "whatsapp", "mensagem", "criado_em")
    fields = ("nome", "whatsapp", "mensagem", "resposta", "criado_em")

    @admin.display(boolean=True, description="Respondida")
    def respondida(self, obj):
        return bool(obj.resposta)

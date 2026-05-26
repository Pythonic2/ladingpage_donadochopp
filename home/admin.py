from django.contrib import admin
from .models import Produto, Pedido, Transacao, Pergunta, Evento, Depoimento

# Register your models here.
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(Transacao)


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

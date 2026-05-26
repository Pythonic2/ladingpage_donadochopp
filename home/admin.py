from django.contrib import admin
from .models import Produto, Pedido, Transacao, Pergunta

# Register your models here.
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(Transacao)


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

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home_view, name="home"),
    path("produto/<int:produto_id>/", produto_detalhe_view, name="produto-detalhe"),
    path("produto/<slug:slug>/", produto_detalhe_view, name="produto-detalhe-slug"),
    path("comprar/<slug:slug>/", cadastrar_usuario_view, name="cadastrar-usuario-slug"),
    path(
        "cadastrar-usuario/<int:produto_id>/",
        cadastrar_usuario_view,
        name="cadastrar-usuario",
    ),
    path("cadastrar-pedido/", cadastrar_pedido, name="cadastrar-pedido"),
    path("pag/", simple_test, name="pagamento"),
    path("sucesso/", sucesso_view, name="sucesso"),
    path("falha/", failure_view, name="falha"),
    path("pendente/", pending_view, name="pendente"),
    path("enviar-pergunta/", enviar_pergunta, name="enviar-pergunta"),
    path("catalogo/", catalogo_instagram, name="catalogo-instagram"),
    path("catalogo/<slug:slug>/", catalogo_instagram_produto, name="catalogo-instagram-produto"),
    path("catalogo-instagram.csv", catalogo_instagram_csv, name="catalogo-instagram-csv"),
    path("catalogo/<slug:slug>.csv", catalogo_instagram_csv_produto, name="catalogo-instagram-csv-produto"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

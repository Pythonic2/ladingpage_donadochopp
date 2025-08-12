from django.urls import path
from .views import home_view, cadastrar_usuario_view, cadastrar_pedido
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', home_view, name='home'),
    path('cadastrar-usuario/<int:produto_id>/', cadastrar_usuario_view, name='cadastrar-usuario'),
    path('cadastrar-pedido/', cadastrar_pedido, name='cadastrar-pedido')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
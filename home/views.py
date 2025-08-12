from django.shortcuts import render, get_object_or_404, redirect
from .forms import PedidoForm
import requests
from .criar_preferencia import criar_preferencia
from .models import Produto
# Create your views here.
def home_view(request):
    produtos = Produto.objects.all()
    return render(request, 'index.html', {'produtos': produtos})


def cadastrar_usuario_view(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.produto = produto
            pedido.save()
            return render(request, 'success.html', {'form': form})
    else:
        form = PedidoForm()
    return render(request, 'cadastrar_user.html', {'form': form, 'produto': produto})

from .criar_preferencia import criar_preferencia

def cadastrar_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        produto_id = request.POST.get('produto_id')
        if form.is_valid() and produto_id:
            pedido = form.save(commit=False)
            produto = Produto.objects.get(id=produto_id)
            pedido.produto = produto
            pedido.save()

            item = [{
                "id": produto.id,
                "title": produto.nome,
                "quantity": pedido.quantidade,
                "currency_id": "BRL",
                "unit_price": float(produto.preco)
            }]
            client_id = pedido.cpf_cliente

            a = criar_preferencia(item, client_id)
            if a and 'init_point' in a:
                return redirect(a['init_point'])
            else:
                # Exibe mensagem de erro amigável
                return render(request, 'erro_pagamento.html', {'mensagem': 'Não foi possível gerar o link de pagamento. Tente novamente.'})
    else:
        form = PedidoForm()
    return render(request, 'cadastrar_pedido.html', {'form': form})
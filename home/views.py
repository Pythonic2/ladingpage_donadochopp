from django.shortcuts import render, get_object_or_404, redirect
from .forms import PedidoForm
import requests
from .criar_preferencia import criar_preferencia
from .models import Produto, Pedido, Transacao
from .busca_pagamento import buscar_pagamento_mercado_pago
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
import logging
from .notificacao import send_email
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
            if a and a.get('init_point'):
                return redirect(a['init_point'])
            else:
                print(form.errors)
                # Exibe mensagem de erro amigável
                return render(request, 'erro_pagamento.html', {'mensagem': 'Não foi possível gerar o link de pagamento. Tente novamente.'})
    else:
        form = PedidoForm()
    return render(request, 'cadastrar_user.html', {'form': form})

@csrf_exempt
def simple_test(request):
    logging.debug("Recebendo requisição POST")

    if request.method == "POST":
        if not request.body:
            logging.warning("Corpo da requisição vazio")
            return JsonResponse({'error': 'Corpo da requisição vazio'}, status=400)

        try:
            # Decodificar o corpo da requisição em JSON
            webhook_data = json.loads(request.body.decode('utf-8'))
            logging.debug(f"Dados recebidos no webhook: {webhook_data}")

            # Capturar o pagamento_id e outras informações do webhook
            pagamento_id = str(webhook_data.get('data', {}).get('id', ''))
            tipo = webhook_data.get('type', {})
            logging.debug(f"Pagamento ID: {pagamento_id}, Tipo: {tipo}")


            logging.info("Dados do webhook salvos em recibo.csv")

            # Buscar pagamento usando a função definida anteriormente
            pag = buscar_pagamento_mercado_pago(pagamento_id)
            logging.debug("################## IFOR PAG ##################")
            logging.debug(f"{pag}")
            logging.debug("####################################")
            logging.debug(f"Informações do pagamento: {pag}")
            logging.debug(f"Informações do tipo do Pagamento: {tipo}, tam {len(tipo)}")
            pd_id = tipo
            status = pag['status']
            try:
                print(f'-----------------{pd_id}-----------------')
                if status == 'approved' and tipo == 'payment':
                    print(f"pag {pag}")
                    print(f"items:{pag['items'][0]}")
                #     logging.debug("Pagamento aprovado, processando transação...")
                    pedido_user = Pedido.objects.get(cpf_cliente=pag['usuario'])
                    user = pedido_user.nome_cliente
                    print(user)
                    transacao = Transacao(
                        pagamento_id=pag['id'],
                        data=pag['data'],
                        valor=pag['valor'],
                        status=pag['status'],
                        payment_type = pag['payment_type'],
                        nome_cliente=pedido_user.nome_cliente,
                        cpf_cliente=pedido_user.cpf_cliente,
                        endereco_cliente=pedido_user.endereco_cliente,
                        telefone_cliente=pedido_user.telefone_cliente,
                        email_cliente=pedido_user.email_cliente,
                        data_nascimento_cliente=pedido_user.data_nascimento_cliente,
                        quantidade=pedido_user.quantidade,
                        data_pedido=pedido_user.data_pedido,
                        cor_produto=pedido_user.cor_produto,
                        logo=pedido_user.logo,
                    )
                    transacao.save()  # Salve primeiro para gerar o ID

                    produto_obj = Produto.objects.get(nome=pag['items'][0])
                    transacao.items.add(produto_obj)
                

                    transacao.save() # Salvar a transação
                    pedido_user.delete()  # Excluir o pedido
                    send_email(
                    subject=f"Nova Compra Realizada",
                    body=(
                        f"Status: {transacao.status}\n"
                        f"Data: {transacao.data}\n"
                        f"ID do Pagamento: {transacao.pagamento_id}\n"
                        f"Tipo de Pagamento: {transacao.payment_type}\n"
                        f"Valor da Compra: {transacao.valor}\n"
                        f"Itens da Compra: {', '.join([str(item) for item in transacao.items.all()])}\n"
                        f"Nome do Cliente: {transacao.nome_cliente}\n"
                        f"CPF do Cliente: {transacao.cpf_cliente}\n"
                        f"E-mail do Cliente: {transacao.email_cliente}\n"
                        f"Telefone do Cliente: {transacao.telefone_cliente}\n"
                        f"Endereço do Cliente: {transacao.endereco_cliente}\n"
                        f"Data de Nascimento: {transacao.data_nascimento_cliente}\n"
                        f"Quantidade: {transacao.quantidade}\n"
                        f"Data do Pedido: {transacao.data_pedido}\n"
                        f"Cor do Produto: {transacao.cor_produto}\n"
                       
                    ),
                    sender_email="noticacoes@gmail.com",
                    sender_password="lqxvsvybjfumjflo",
                    recipient_emails=[
                        "igoormarinhosilva@gmail.com",
                        "donadochopp@gmail.com",
                        
                    ]
                )
                    logging.info(f"E-mail enviado para notificações")
                    return JsonResponse({'status': 'success'})
                else:
                    print(status)
                    logging.warning("Tipo de pagamento diferente de 'payment' ou ID não encontrado.")
                    return JsonResponse({'status': 'Order Generate'})
            except Exception as e:
                logging.warning(f"Erro ao processar transação: {str(e)}")
                return JsonResponse({'status': 'Order Generate'})

        except json.JSONDecodeError:
            logging.error("Falha ao decodificar JSON")
            return JsonResponse({'error': 'Falha ao decodificar JSON'}, status=400)
        # except Usuario.DoesNotExist:
        #     logging.error("Usuário não encontrado")
        #     return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        except Produto.DoesNotExist:
            logging.error("Produto não encontrado")
            return JsonResponse({'error': 'Produto não encontrado'}, status=404)

    logging.warning("Método HTTP não permitido")
    return JsonResponse({'status': 'method_not_allowed'}, status=405)


def sucesso_view(request):
    payment_id = request.GET.get('payment_id')
    # Você pode passar para o template se quiser exibir ou processar
    return render(request, 'sucesso.html', {'payment_id': payment_id})

def failure_view(request):
    return render(request, 'failure.html')

def pending_view(request):
    return render(request, 'pending.html')
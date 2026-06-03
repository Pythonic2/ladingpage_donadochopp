from django.shortcuts import render, get_object_or_404, redirect
from .forms import PedidoForm
from .criar_preferencia import criar_preferencia
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
)
from .busca_pagamento import buscar_pagamento_mercado_pago
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Prefetch
import json
import logging
from .notificacao import send_email


# Create your views here.
def paginar_perguntas(request):
    paginator = Paginator(Pergunta.objects.all(), 3)
    page_number = request.GET.get("page", 1)
    return paginator.get_page(page_number)


class SecaoFixaPadrao:
    def __init__(self, ordem, ativo=True, titulo="", etiqueta="", descricao="", tipo=""):
        self.ordem = ordem
        self.ativo = ativo
        self.titulo = titulo
        self.etiqueta = etiqueta
        self.descricao = descricao
        self.tipo = tipo


def secoes_fixas_landing(secoes):
    defaults = {
        "hero_principal": SecaoFixaPadrao(0, tipo="hero_principal"),
        "barra_confianca": SecaoFixaPadrao(5, tipo="barra_confianca"),
        "produtos": SecaoFixaPadrao(10, tipo="produtos"),
        "eventos": SecaoFixaPadrao(30, tipo="eventos"),
        "passos": SecaoFixaPadrao(40, tipo="passos"),
        "beneficios": SecaoFixaPadrao(50, tipo="beneficios"),
        "video": SecaoFixaPadrao(60, tipo="video"),
        "depoimentos": SecaoFixaPadrao(70, tipo="depoimentos"),
        "personalizar": SecaoFixaPadrao(80, tipo="personalizar"),
        "prova_social": SecaoFixaPadrao(90, tipo="prova_social"),
        "galeria": SecaoFixaPadrao(100, tipo="galeria"),
        "faq": SecaoFixaPadrao(110, tipo="faq"),
        "contato": SecaoFixaPadrao(120, tipo="contato"),
        "fechamento": SecaoFixaPadrao(130, tipo="fechamento"),
        "logo_header": SecaoFixaPadrao(140, tipo="logo_header"),
        "logo_footer": SecaoFixaPadrao(150, tipo="logo_footer"),
    }
    defaults.update({secao.tipo: secao for secao in secoes if secao.tipo in defaults})
    return defaults


def primeira_midia_por_papel(midias, papeis):
    papeis_normalizados = {papel.lower() for papel in papeis}
    for midia in midias:
        papel = (getattr(midia, "papel", "") or "").lower()
        descricao = (getattr(midia, "descricao", "") or "").lower()
        titulo = (getattr(midia, "titulo", "") or "").lower()
        if papel in papeis_normalizados:
            return midia
        if any(marcador in descricao or marcador in titulo for marcador in papeis_normalizados):
            return midia
    return None


def midias_de_galeria(midias):
    papeis_excluidos = {"desktop", "mobile", "logo_header", "capa"}
    return [
        midia
        for midia in midias
        if getattr(midia, "tipo", "imagem") == "imagem"
        and (getattr(midia, "papel", "") or "principal") not in papeis_excluidos
    ]


def home_view(request):
    produtos = Produto.objects.all()
    eventos = Evento.objects.filter(ativo=True)
    depoimentos = Depoimento.objects.filter(ativo=True)
    todas_secoes = list(
        SecaoLanding.objects.all()
        .prefetch_related(
            Prefetch(
                "midias",
                queryset=SecaoLandingMidia.objects.filter(ativo=True).order_by(
                    "ordem", "id"
                ),
            ),
            Prefetch("cards", queryset=SecaoLandingCard.objects.filter(ativo=True)),
            Prefetch(
                "linhas_tabela",
                queryset=SecaoLandingLinhaTabela.objects.filter(ativo=True),
            ),
        )
    )
    secoes_landing = [
        secao
        for secao in todas_secoes
        if secao.ativo and secao.tipo in ("metricas_tabela", "painel_destaque")
    ]
    blocos_fixos = secoes_fixas_landing(todas_secoes)
    for secao in todas_secoes:
        if hasattr(secao, "midias"):
            secao.midias_galeria = midias_de_galeria(list(secao.midias.all()))
    midias = MidiaLanding.objects.filter(ativo=True)
    midias_por_chave = {}
    for midia in midias:
        midias_por_chave.setdefault(midia.chave, []).append(midia)
    midias_secao = {
        chave: list(bloco.midias.filter(ativo=True).order_by("ordem", "id"))
        if getattr(bloco, "ativo", False) and hasattr(bloco, "midias_ativas")
        else []
        for chave, bloco in blocos_fixos.items()
    }
    video_secao = midias_secao.get("video", [])
    video_thumb_secao = [midia for midia in video_secao if midia.tipo == "imagem" or midia.papel == "capa"]
    video_principal_secao = [midia for midia in video_secao if midia.tipo == "video"]
    hero_midias = midias_secao.get("hero_principal") or midias_por_chave.get("hero_principal", [])
    hero_desktop = primeira_midia_por_papel(hero_midias, ("desktop", "principal")) or (hero_midias[0] if hero_midias else None)
    hero_mobile = primeira_midia_por_papel(hero_midias, ("mobile",)) or hero_desktop
    logo_header_midias = (
        midias_secao.get("logo_header")
        or midias_por_chave.get("logo_header", [])
        or midias_secao.get("logo_footer")
        or midias_por_chave.get("logo_footer", [])
    )
    logo_header_desktop = primeira_midia_por_papel(logo_header_midias, ("desktop", "logo_header", "principal")) or (
        logo_header_midias[0] if logo_header_midias else None
    )
    logo_header_mobile = primeira_midia_por_papel(logo_header_midias, ("mobile",)) or logo_header_desktop
    midias_extras_secao = {
        chave: midias_de_galeria(midias)
        for chave, midias in midias_secao.items()
    }
    perguntas = paginar_perguntas(request)
    return render(
        request,
        "landing_new.html",
        {
            "produtos": produtos,
            "config_landing": ConfiguracaoLanding.get_solo(),
            "eventos": eventos,
            "eventos_midia": midias_extras_secao.get("eventos", []),
            "barra_confianca_midia": midias_extras_secao.get("barra_confianca", []),
            "produtos_midia": midias_extras_secao.get("produtos", []),
            "passos_midia": midias_extras_secao.get("passos", []),
            "beneficios_midia": midias_extras_secao.get("beneficios", []),
            "video_midia_extra": midias_extras_secao.get("video", []),
            "personalizar_midia": midias_extras_secao.get("personalizar", []),
            "faq_midia": midias_extras_secao.get("faq", []),
            "contato_midia": midias_extras_secao.get("contato", []),
            "fechamento_midia": midias_extras_secao.get("fechamento", []),
            "depoimentos": depoimentos,
            "secoes_landing": secoes_landing,
            "blocos_fixos": blocos_fixos,
            "hero_principal": hero_midias,
            "hero_desktop": hero_desktop,
            "hero_mobile": hero_mobile,
            "logo_header_desktop": logo_header_desktop,
            "logo_header_mobile": logo_header_mobile,
            "lucro_operacao": midias_por_chave.get("lucro_operacao", []),
            "video_thumb": video_thumb_secao or midias_por_chave.get("video_thumb", []),
            "video_principal": video_principal_secao or midias_por_chave.get("video_principal", []),
            "prova_social": midias_secao.get("prova_social") or midias_por_chave.get("prova_social", []),
            "galeria": midias_secao.get("galeria") or midias_por_chave.get("galeria", []),
            "logo_footer": midias_secao.get("logo_footer") or midias_por_chave.get("logo_footer", []),
            "perguntas": perguntas,
        },
    )


def enviar_pergunta(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        whatsapp = request.POST.get("whatsapp", "").strip()
        mensagem = request.POST.get("mensagem", "").strip()
        if nome and whatsapp and mensagem:
            Pergunta.objects.create(nome=nome, whatsapp=whatsapp, mensagem=mensagem)
        perguntas = paginar_perguntas(request)
        return render(request, "partials/perguntas.html", {"perguntas": perguntas})
    perguntas = paginar_perguntas(request)
    return render(request, "partials/perguntas.html", {"perguntas": perguntas})


def produto_detalhe_view(request, produto_id=None, slug=None):
    if slug:
        produto = get_object_or_404(Produto, slug=slug)
    else:
        produto = get_object_or_404(Produto, id=produto_id)
    outros_produtos = Produto.objects.exclude(id=produto_id)[:3]
    return render(
        request,
        "produto_detalhe.html",
        {
            "produto": produto,
            "outros_produtos": outros_produtos,
        },
    )


def cadastrar_usuario_view(request, produto_id=None, slug=None):
    if slug:
        produto = get_object_or_404(Produto, slug=slug)
    else:
        produto = get_object_or_404(Produto, id=produto_id)
    if request.method == "POST":
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.produto = produto
            pedido.save()
            return render(request, "success.html", {"form": form})
    else:
        form = PedidoForm()
    return render(
        request,
        "cadastrar_user.html",
        {
            "form": form,
            "produto": produto,
            "config_landing": ConfiguracaoLanding.get_solo(),
        },
    )


def cadastrar_pedido(request):
    if request.method == "POST":
        form = PedidoForm(request.POST, request.FILES)
        produto_id = request.POST.get("produto_id")
        if form.is_valid() and produto_id:
            pedido = form.save(commit=False)
            produto = Produto.objects.get(id=produto_id)
            pedido.produto = produto
            pedido.save()

            item = [
                {
                    "id": produto.id,
                    "title": produto.nome,
                    "quantity": pedido.quantidade,
                    "currency_id": "BRL",
                    "unit_price": float(produto.preco),
                }
            ]
            client_id = str(pedido.id)

            a = criar_preferencia(item, client_id)
            checkout_url = a.get("init_point") or a.get("sandbox_init_point") if a else None
            if checkout_url:
                return redirect(checkout_url)
            else:
                print(form.errors)
                # Exibe mensagem de erro amigável
                return render(
                    request,
                    "erro_pagamento.html",
                    {
                        "mensagem": "Não foi possível gerar o link de pagamento. Tente novamente.",
                        "detalhe": a,
                    },
                )
        if produto_id:
            produto = get_object_or_404(Produto, id=produto_id)
            return render(
                request,
                "cadastrar_user.html",
                {
                    "form": form,
                    "produto": produto,
                    "config_landing": ConfiguracaoLanding.get_solo(),
                },
            )
    else:
        form = PedidoForm()
    return render(request, "cadastrar_user.html", {"form": form})


@csrf_exempt
def simple_test(request):
    logging.debug("Recebendo requisição POST")

    if request.method == "POST":
        if not request.body:
            logging.warning("Corpo da requisição vazio")
            return JsonResponse({"error": "Corpo da requisição vazio"}, status=400)

        try:
            # Decodificar o corpo da requisição em JSON
            webhook_data = json.loads(request.body.decode("utf-8"))
            logging.debug(f"Dados recebidos no webhook: {webhook_data}")

            # Capturar o pagamento_id e outras informações do webhook
            pagamento_id = str(webhook_data.get("data", {}).get("id", ""))
            tipo = webhook_data.get("type", {})
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
            print(pag)
            if not pag:
                logging.warning(
                    "Pagamento não encontrado para o ID %s. Encerrando webhook sem erro.",
                    pagamento_id,
                )
                return JsonResponse(
                    {"ok": False, "message": "Pagamento não encontrado"},
                    status=200,
                )
            status = pag["status"]
            try:
                print(f"-----------------{pd_id}-----------------")
                if status == "approved" and tipo == "payment":
                    print(f"pag {pag}")
                    print(f"items:{pag['items'][0]}")
                    #     logging.debug("Pagamento aprovado, processando transação...")
                    referencia_pedido = str(pag.get("usuario") or "")
                    pedido_user = None
                    if referencia_pedido.isdigit():
                        pedido_user = Pedido.objects.filter(id=referencia_pedido).first()
                    if not pedido_user:
                        pedido_user = (
                            Pedido.objects.filter(cpf_cliente=referencia_pedido)
                            .order_by("-data_pedido", "-id")
                            .first()
                        )
                    if not pedido_user:
                        raise Pedido.DoesNotExist(
                            f"Pedido não encontrado para a referência {referencia_pedido}"
                        )
                    user = pedido_user.nome_cliente
                    print(user)
                    transacao = Transacao(
                        pagamento_id=pag["id"],
                        data=pag["data"],
                        valor=pag["valor"],
                        status=pag["status"],
                        payment_type=pag["payment_type"],
                        nome_cliente=pedido_user.nome_cliente,
                        cpf_cliente=pedido_user.cpf_cliente,
                        endereco_cliente=pedido_user.endereco_cliente,
                        cep_cliente=pedido_user.cep_cliente,
                        tipo_entrega=pedido_user.tipo_entrega,
                        capital_retirada=pedido_user.capital_retirada,
                        telefone_cliente=pedido_user.telefone_cliente,
                        email_cliente=pedido_user.email_cliente,
                        data_nascimento_cliente=pedido_user.data_nascimento_cliente,
                        quantidade=pedido_user.quantidade,
                        data_pedido=pedido_user.data_pedido,
                        cor_produto=pedido_user.cor_produto,
                        logo=pedido_user.logo,
                    )
                    transacao.save()  # Salve primeiro para gerar o ID

                    produto_obj = Produto.objects.get(nome=pag["items"][0])
                    transacao.items.add(produto_obj)

                    transacao.save()  # Salvar a transação
                    #pedido_user.delete()  # Excluir o pedido
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
                            f"CEP da Capital: {transacao.cep_cliente}\n"
                            f"Tipo de Entrega: {transacao.tipo_entrega}\n"
                            f"Capital de Retirada: {transacao.capital_retirada}\n"
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
                        ],
                    )
                    logging.info(f"E-mail enviado para notificações")
                    return JsonResponse({"status": "success"})
                else:
                    print(status)
                    logging.warning(
                        "Tipo de pagamento diferente de 'payment' ou ID não encontrado."
                    )
                    return JsonResponse({"status": "Order Generate"})
            except Exception as e:
                logging.warning(f"Erro ao processar transação: {str(e)}")
                return JsonResponse({"status": "Order Generate"})

        except json.JSONDecodeError:
            logging.error("Falha ao decodificar JSON")
            return JsonResponse({"error": "Falha ao decodificar JSON"}, status=400)
        # except Usuario.DoesNotExist:
        #     logging.error("Usuário não encontrado")
        #     return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
        except Produto.DoesNotExist:
            logging.error("Produto não encontrado")
            return JsonResponse({"error": "Produto não encontrado"}, status=404)

    logging.warning("Método HTTP não permitido")
    return JsonResponse({"status": "method_not_allowed"}, status=405)


def sucesso_view(request):
    payment_id = request.GET.get("payment_id")
    # Você pode passar para o template se quiser exibir ou processar
    return render(request, "sucesso.html", {"payment_id": payment_id})


def failure_view(request):
    return render(request, "faliure.html")


def pending_view(request):
    return render(request, "pending.html")

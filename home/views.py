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
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Prefetch
import csv
import html
import json
import logging
from django.utils.html import strip_tags
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
        outros_produtos = Produto.objects.exclude(id=produto.id)[:3]
    else:
        produto = get_object_or_404(Produto, id=produto_id)
        outros_produtos = Produto.objects.exclude(id=produto.id)[:3]
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
        form = PedidoForm(request.POST, request.FILES, produto=produto)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.produto = produto
            pedido.save()
            return render(request, "success.html", {"form": form})
    else:
        form = PedidoForm(produto=produto)
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
        produto_id = request.POST.get("produto_id")
        produto = get_object_or_404(Produto, id=produto_id) if produto_id else None
        form = PedidoForm(request.POST, request.FILES, produto=produto)
        if form.is_valid() and produto_id:
            pedido = form.save(commit=False)
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
            pagamento_id = str(webhook_data.get("data", {}).get("id") or "").strip()
            tipo = webhook_data.get("type", {})
            logging.debug(f"Pagamento ID: {pagamento_id}, Tipo: {tipo}")

            logging.info("Dados do webhook salvos em recibo.csv")

            if not pagamento_id:
                logging.warning(
                    "Webhook recebido sem ID de pagamento. Payload ignorado: %s",
                    webhook_data,
                )
                return JsonResponse(
                    {"status": "ignored", "message": "payment_id ausente"},
                    status=200,
                )

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
            if pag.get("erro"):
                logging.warning(
                    "Erro retornado pelo Mercado Pago para o pagamento %s: %s",
                    pagamento_id,
                    pag,
                )
                return JsonResponse(
                    {
                        "ok": False,
                        "message": "Erro ao consultar pagamento no Mercado Pago",
                        "payment_id": pagamento_id,
                        "mp_status": pag.get("mp_status"),
                        "mp_response": pag.get("mp_response"),
                    },
                    status=200,
                )
            status = pag["status"]
            try:
                print(f"-----------------{pd_id}-----------------")
                if status == "approved" and tipo == "payment":
                    print(f"pag {pag}")
                    print(f"items:{pag['items'][0]}")
                    pagamento_mp_id = str(pag["id"])
                    transacao_existente = Transacao.objects.filter(
                        pagamento_id=pagamento_mp_id
                    ).first()
                    if transacao_existente:
                        logging.info(
                            "Transação %s já processada. Encerrando webhook.",
                            pagamento_mp_id,
                        )
                        return JsonResponse(
                            {
                                "status": "already_processed",
                                "pagamento_id": pagamento_mp_id,
                            }
                        )
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
                        logging.warning(
                            "Pedido não encontrado para a referência %s do pagamento %s.",
                            referencia_pedido,
                            pagamento_mp_id,
                        )
                        return JsonResponse(
                            {
                                "status": "pedido_not_found",
                                "external_reference": referencia_pedido,
                                "pagamento_id": pagamento_mp_id,
                            }
                        )
                    user = pedido_user.nome_cliente
                    print(user)
                    transacao = Transacao(
                        pagamento_id=pagamento_mp_id,
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
                        produto_variacao_nome=(
                            pedido_user.produto_variacao.nome
                            if pedido_user.produto_variacao
                            else ""
                        ),
                        cor_produto=pedido_user.cor_produto,
                        logo=pedido_user.logo,
                    )
                    transacao.save()  # Salve primeiro para gerar o ID

                    transacao.items.add(pedido_user.produto)

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
                            f"Variação do Produto: {transacao.produto_variacao_nome or 'Não selecionada'}\n"
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


def catalogo_instagram(request):
    """
    Feed de produtos no formato Meta/Facebook Product Catalog.
    Cadastre esta URL no Gerenciador de Comércio do Facebook/Instagram:
    https://vendas.donadochopp.com.br/catalogo/
    """
    produtos = Produto.objects.filter(estoque__gt=0)
    items = []
    for p in produtos:
        imagem_url = request.build_absolute_uri(p.imagem_segura_url)
        link_url = request.build_absolute_uri(p.get_absolute_url())

        preco_formatado = f"{p.preco:.2f} BRL"
        item = {
            "id": str(p.id),
            "title": p.nome,
            "description": p.descricao,
            "availability": "in stock" if p.estoque > 0 else "out of stock",
            "condition": "new",
            "price": preco_formatado,
            "link": link_url,
            "image_link": imagem_url,
            "brand": "Dona do Chopp",
        }
        if p.preco_sem_desconto and p.preco_sem_desconto > p.preco:
            item["sale_price"] = preco_formatado
            item["price"] = f"{p.preco_sem_desconto:.2f} BRL"
        items.append(item)

    return JsonResponse({"data": items})


def catalogo_instagram_produto(request, slug):
    """
    Retorna um único produto pelo slug no formato Meta Product Catalog.
    URL: /catalogo/<slug>/
    """
    produto = get_object_or_404(Produto, slug=slug)
    imagem_url = request.build_absolute_uri(produto.imagem_segura_url)
    link_url = request.build_absolute_uri(produto.get_absolute_url())

    preco_formatado = f"{produto.preco:.2f} BRL"
    item = {
        "id": str(produto.id),
        "title": produto.nome,
        "description": produto.descricao,
        "availability": "in stock" if produto.estoque > 0 else "out of stock",
        "condition": "new",
        "price": preco_formatado,
        "link": link_url,
        "image_link": imagem_url,
        "brand": "Dona do Chopp",
    }
    if produto.preco_sem_desconto and produto.preco_sem_desconto > produto.preco:
        item["sale_price"] = preco_formatado
        item["price"] = f"{produto.preco_sem_desconto:.2f} BRL"

    return JsonResponse({"data": [item]})


def _limpar_html(valor):
    if not valor:
        return ""
    texto = strip_tags(valor)
    texto = html.unescape(texto)
    return " ".join(texto.split())


def catalogo_instagram_csv(request):
    """
    Feed CSV no formato Meta/Facebook Product Catalog.
    Cadastre no Commerce Manager > Fontes de dados > Feed de dados > URL:
    https://vendas.donadochopp.com.br/catalogo-instagram.csv
    """
    produtos = Produto.objects.filter(estoque__gt=0).order_by("id")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'inline; filename="catalogo-instagram.csv"'
    response.write("\ufeff")  # BOM UTF-8 para compatibilidade

    writer = csv.writer(response)
    writer.writerow([
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand", "sale_price",
    ])

    for p in produtos:
        link = request.build_absolute_uri(p.get_absolute_url())
        imagem = request.build_absolute_uri(p.imagem.url) if p.imagem and p.imagem.name else ""
        preco = f"{p.preco:.2f} BRL"
        sale_price = ""

        if p.preco_sem_desconto and p.preco_sem_desconto > p.preco:
            sale_price = preco
            preco = f"{p.preco_sem_desconto:.2f} BRL"

        writer.writerow([
            str(p.id),
            p.nome,
            _limpar_html(p.descricao),
            "in stock",
            "new",
            preco,
            link,
            imagem,
            "Dona do Chopp",
            sale_price,
        ])

    return response


def catalogo_instagram_csv_produto(request, slug):
    """
    CSV de um único produto pelo slug. Use para cadastrar um produto
    de cada vez no Instagram Shopping:
    https://vendas.donadochopp.com.br/catalogo/<slug>.csv
    """
    p = get_object_or_404(Produto, slug=slug)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'inline; filename="{p.slug}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)
    writer.writerow([
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand", "sale_price",
    ])

    link = request.build_absolute_uri(p.get_absolute_url())
    imagem = request.build_absolute_uri(p.imagem.url) if p.imagem and p.imagem.name else ""
    preco = f"{p.preco:.2f} BRL"
    sale_price = ""

    if p.preco_sem_desconto and p.preco_sem_desconto > p.preco:
        sale_price = preco
        preco = f"{p.preco_sem_desconto:.2f} BRL"

    writer.writerow([
        str(p.id),
        p.nome,
        _limpar_html(p.descricao),
        "in stock" if p.estoque > 0 else "out of stock",
        "new",
        preco,
        link,
        imagem,
        "Dona do Chopp",
        sale_price,
    ])

    return response

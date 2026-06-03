from django.db import migrations


SECTION_CARDS = {
    "barra_confianca": [
        ("Frete grátis no aeroporto das capitais", "", ""),
        ("Garantia de 1 ano", "", ""),
        ("10x sem juros", "", ""),
        ("Suporte do zero", "", ""),
        ("Equipamento testado", "", ""),
    ],
    "eventos": [
        ("Qualquer lugar", "Rua, praia, salão", ""),
        ("Qualquer hora", "Pico e evento", ""),
        ("Mais giro", "Venda na hora", ""),
    ],
    "passos": [
        ("Você escolhe o modelo", "1", "Defina cores, estilo e envie sua logomarca para personalização."),
        ("A gente fabrica e envia", "2", "Produção sob medida, teste do equipamento e envio com segurança."),
        ("Você começa a vender", "3", "Recebe orientação para instalação, uso e primeiros passos no chopp."),
    ],
    "beneficios": [
        ("Entrega Rápida para Todo Brasil", "", "Receba sua chopeira bomba de gasolina com agilidade e segurança. Produção otimizada e logística eficiente para entregar em até 15 dias úteis."),
        ("Referência Nacional no Segmento", "", "Somos a única fabricante de chopeira bomba de gasolina que também atua diariamente na venda de chopp em praias, eventos e ações comerciais."),
        ("Suporte Completo do Zero ao Lucro", "", "Ensinamos montagem, conexões, compra de barris, operação correta, precificação e estratégias de vendas para começar com segurança."),
        ("Qualidade Testada em Operação Real", "", "Nossos equipamentos são utilizados e testados diariamente em operações reais de venda de chopp, garantindo mais durabilidade, eficiência e desempenho."),
        ("Pistola que realmente funciona", "", "Pistola de abastecimento em inox 304, própria para contato com bebidas, que entrega chopp ao invés de somente espuma e cria uma experiência mais realista."),
        ("Garantia Real de 1 Ano", "", "Garantia completa de 12 meses para funcionamento total do equipamento, com substituição de peças em caso de defeito de fabricação."),
    ],
    "faq": [
        ("Quanto tempo leva para receber minha chopeira?", "", "O prazo é de até 15 dias úteis para todo o Brasil. O envio é feito com rastreamento e embalagem reforçada."),
        ("Posso personalizar com minha marca?", "", "Sim. Você escolhe as cores e envia sua logomarca. A personalização faz parte da proposta da Dona do Chopp."),
        ("Preciso ter experiência com chopp?", "", "Não. Você recebe orientação sobre instalação, conexões, compra do chopp e operação inicial."),
        ("Quais formas de pagamento aceitam?", "", "PIX com desconto, cartão de crédito em até 10x sem juros, boleto e transferência."),
        ("E se der problema?", "", "Todas as chopeiras possuem garantia de 1 ano para defeitos de fabricação, com suporte para substituição de peças quando necessário."),
    ],
}


SECTION_UPDATES = {
    "produtos": {
        "destaque_etiqueta": "Quer uma cor, marca ou combo diferente?",
        "destaque_valor": "Fabricamos sua chopeira sob medida.",
        "destaque_observacao": "Solicitar orçamento",
    },
    "beneficios": {
        "etiqueta": "Por que escolher a Dona do Chopp?",
        "titulo": "Você compra um negócio validado, não apenas uma chopeira.",
        "texto_final": "Você não compra apenas uma chopeira. Investe em um produto validado, lucrativo e respaldado por quem realmente entende do mercado de chopp.",
    },
}


def seed_modular_copy(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLandingCard = apps.get_model("home", "SecaoLandingCard")

    for tipo, fields in SECTION_UPDATES.items():
        SecaoLanding.objects.filter(tipo=tipo).update(**fields)

    secoes = {secao.tipo: secao for secao in SecaoLanding.objects.filter(tipo__in=SECTION_CARDS.keys())}
    for tipo, cards in SECTION_CARDS.items():
        secao = secoes.get(tipo)
        if not secao:
            continue
        for ordem, (titulo, valor, descricao) in enumerate(cards):
            SecaoLandingCard.objects.get_or_create(
                secao=secao,
                titulo=titulo,
                defaults={
                    "valor": valor,
                    "descricao": descricao,
                    "ordem": ordem,
                    "ativo": True,
                },
            )


def unseed_modular_copy(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLandingCard = apps.get_model("home", "SecaoLandingCard")
    titles = [titulo for cards in SECTION_CARDS.values() for titulo, _valor, _descricao in cards]
    SecaoLandingCard.objects.filter(titulo__in=titles).delete()
    SecaoLanding.objects.filter(tipo="produtos").update(
        destaque_etiqueta="",
        destaque_valor="",
        destaque_observacao="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0026_landing_header_media_roles"),
    ]

    operations = [
        migrations.RunPython(seed_modular_copy, unseed_modular_copy),
    ]

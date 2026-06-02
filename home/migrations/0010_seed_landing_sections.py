from django.db import migrations


def seed_landing_sections(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLandingCard = apps.get_model("home", "SecaoLandingCard")
    SecaoLandingLinhaTabela = apps.get_model("home", "SecaoLandingLinhaTabela")

    lucro, _ = SecaoLanding.objects.update_or_create(
        slug="lucro",
        defaults={
            "ancora": "lucro",
            "tipo": "metricas_tabela",
            "etiqueta": "Máquina de fazer dinheiro",
            "titulo": "Por que chamam a chopeira bomba de combustível de máquina de fazer dinheiro?",
            "descricao": "Não é apenas uma chopeira, é um modelo de negócio validado. Veja como os números trabalham a seu favor:",
            "texto_final": "Potencial de escala: quantos barris você consegue vender no seu final de semana?",
            "observacao": "Valores são exemplos de faturamento bruto e podem variar conforme região, preço de venda, custos, operação e volume de trabalho.",
            "imagem_titulo": "Operação Dona do Chopp",
            "cabecalho_tabela_esquerda": "Unidade de negócio",
            "cabecalho_tabela_direita": "Projeção",
            "fundo": "branco",
            "cor_titulo": "vermelho",
            "ordem": 20,
            "ativo": True,
        },
    )

    for index, card in enumerate(
        [
            {
                "titulo": "Capacidade de entrega",
                "valor": "166 copos",
                "descricao": "1 barril de 50L rende 166 copos de 300ml.",
            },
            {
                "titulo": "Faturamento bruto",
                "valor": "R$ 2.158",
                "descricao": "Vendendo cada copo por R$ 13,00.",
            },
        ]
    ):
        SecaoLandingCard.objects.update_or_create(
            secao=lucro,
            titulo=card["titulo"],
            defaults={**card, "ordem": index, "ativo": True},
        )

    for index, linha in enumerate(
        [
            {"rotulo": "1 Copo (300ml)", "valor": "R$ 13,00", "destacar": False},
            {"rotulo": "100 Copos", "valor": "R$ 1.300,00", "destacar": False},
            {"rotulo": "1 Barril (166 copos)", "valor": "R$ 2.158,00", "destacar": False},
            {"rotulo": "4 Barris (média de final de semana)", "valor": "R$ 8.632,00", "destacar": True},
        ]
    ):
        SecaoLandingLinhaTabela.objects.update_or_create(
            secao=lucro,
            rotulo=linha["rotulo"],
            defaults={**linha, "ordem": index, "ativo": True},
        )

    eventos, _ = SecaoLanding.objects.update_or_create(
        slug="eventos-privados",
        defaults={
            "ancora": "eventos-privados",
            "tipo": "painel_destaque",
            "etiqueta": "Fature alto com eventos privados",
            "titulo": "Ouro Líquido em Casamentos e Aniversários",
            "descricao": "Não limite seu ganho apenas à venda por copo. O mercado de eventos sociais é uma mina de ouro para quem possui a Dona do Chopp.",
            "destaque_etiqueta": "Exemplo em uma única noite",
            "destaque_valor": "R$ 4.200",
            "destaque_descricao": "Festa para 80 pessoas com 3 barris de chopp.",
            "destaque_observacao": "Sua máquina pode se pagar em apenas 3 ou 4 eventos deste porte.",
            "fundo": "marrom",
            "cor_titulo": "amarelo",
            "ordem": 21,
            "ativo": True,
        },
    )

    for index, card in enumerate(
        [
            {
                "titulo": "Pacotes completos",
                "descricao": "Em casamentos, aniversários e eventos corporativos, o cliente compra a experiência.",
            },
            {
                "titulo": "Ticket elevado",
                "descricao": "Um único evento pode contratar 2, 3 ou até 5 barris.",
            },
            {
                "titulo": "Lucro por contrato",
                "descricao": "Cada barril para evento sai, em média, por R$ 1.400,00.",
            },
        ]
    ):
        SecaoLandingCard.objects.update_or_create(
            secao=eventos,
            titulo=card["titulo"],
            defaults={**card, "ordem": index, "ativo": True},
        )


def remove_landing_sections(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLanding.objects.filter(slug__in=["lucro", "eventos-privados"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_secaolanding_secaolandingcard_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_landing_sections, remove_landing_sections),
    ]

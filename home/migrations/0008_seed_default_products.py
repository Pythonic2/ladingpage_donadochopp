from decimal import Decimal

from django.db import migrations


DEFAULT_PRODUCTS = [
    {
        "nome": "Chopeira + Kit Extração",
        "descricao": (
            "<p>Chopeira personalizada no estilo bomba de gasolina, pronta para operação "
            "com kit extração para começar a vender chopp com presença e praticidade.</p>"
        ),
        "preco": Decimal("11990.00"),
        "preco_sem_desconto": Decimal("12990.00"),
        "estoque": 5,
        "peso": Decimal("10.00"),
        "altura": Decimal("10.00"),
        "largura": Decimal("10.00"),
        "comprimento": Decimal("10.00"),
        "cep_origem": "58074158",
        "imagem": "produtos/bomba2.png",
    },
    {
        "nome": "Carrinho Completo",
        "descricao": (
            "<p>Carrinho completo com chopeira personalizada e estrutura para operação "
            "em eventos, praia e pontos de venda com mais impacto visual.</p>"
        ),
        "preco": Decimal("14990.00"),
        "preco_sem_desconto": Decimal("15990.00"),
        "estoque": 10,
        "peso": Decimal("28.00"),
        "altura": Decimal("200.00"),
        "largura": Decimal("70.00"),
        "comprimento": Decimal("130.00"),
        "cep_origem": "60410305",
        "imagem": "produtos/fullcombo.png",
    },
]


def seed_default_products(apps, schema_editor):
    Produto = apps.get_model("home", "Produto")

    for product_data in DEFAULT_PRODUCTS:
        Produto.objects.get_or_create(
            nome=product_data["nome"],
            defaults=product_data,
        )


def remove_seeded_products(apps, schema_editor):
    Produto = apps.get_model("home", "Produto")
    Produto.objects.filter(nome__in=[item["nome"] for item in DEFAULT_PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_midialanding"),
    ]

    operations = [
        migrations.RunPython(seed_default_products, remove_seeded_products),
    ]

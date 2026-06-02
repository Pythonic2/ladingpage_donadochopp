from django.db import migrations


DEFAULT_BLOCKS = [
    ("barra_confianca", 5),
    ("produtos", 10),
    ("eventos", 30),
    ("passos", 40),
    ("beneficios", 50),
    ("video", 60),
    ("depoimentos", 70),
    ("personalizar", 80),
    ("prova_social", 90),
    ("galeria", 100),
    ("faq", 110),
    ("contato", 120),
    ("fechamento", 130),
]


def seed_fixed_landing_blocks(apps, schema_editor):
    BlocoFixoLanding = apps.get_model("home", "BlocoFixoLanding")
    for chave, ordem in DEFAULT_BLOCKS:
        BlocoFixoLanding.objects.get_or_create(
            chave=chave,
            defaults={
                "ordem": ordem,
                "ativo": True,
            },
        )


def remove_fixed_landing_blocks(apps, schema_editor):
    BlocoFixoLanding = apps.get_model("home", "BlocoFixoLanding")
    BlocoFixoLanding.objects.filter(chave__in=[chave for chave, _ordem in DEFAULT_BLOCKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0012_blocofixolanding"),
    ]

    operations = [
        migrations.RunPython(seed_fixed_landing_blocks, remove_fixed_landing_blocks),
    ]

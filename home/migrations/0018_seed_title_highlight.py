from django.db import migrations


def seed_title_highlight(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    SecaoLanding.objects.filter(tipo="hero_principal").update(
        titulo_destaque="A Máquina de Fazer Dinheiro",
        cor_titulo_destaque="verde",
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0017_secaolanding_cor_titulo_destaque_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_title_highlight, noop_reverse),
    ]

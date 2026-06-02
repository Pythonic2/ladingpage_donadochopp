from django.db import migrations


COLOR_MAP = {
    "verde": "#169b4f",
    "vermelho": "#df2f24",
    "amarelo": "#ffc247",
    "marrom": "#20130f",
    "branco": "#ffffff",
}


def normalize_colors(apps, schema_editor):
    SecaoLanding = apps.get_model("home", "SecaoLanding")
    for old_value, new_value in COLOR_MAP.items():
        SecaoLanding.objects.filter(cor_titulo_destaque=old_value).update(
            cor_titulo_destaque=new_value
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0019_alter_secaolanding_cor_titulo_destaque"),
    ]

    operations = [
        migrations.RunPython(normalize_colors, noop_reverse),
    ]

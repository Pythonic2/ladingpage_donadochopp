from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_pergunta_resposta"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="cep_cliente",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
        migrations.AddField(
            model_name="transacao",
            name="cep_cliente",
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]

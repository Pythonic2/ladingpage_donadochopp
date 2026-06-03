from django.db import migrations, models


def preencher_contato_obrigatorio(apps, schema_editor):
    Pedido = apps.get_model("home", "Pedido")
    for pedido in Pedido.objects.all():
        changed = False
        if not pedido.email_cliente:
            pedido.email_cliente = f"sem-email-pedido-{pedido.pk}@example.invalid"
            changed = True
        if not pedido.cep_cliente:
            pedido.cep_cliente = "00000-000"
            changed = True
        if changed:
            pedido.save(update_fields=["email_cliente", "cep_cliente"])


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0027_seed_modular_landing_copy"),
    ]

    operations = [
        migrations.RunPython(preencher_contato_obrigatorio, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="pedido",
            name="cpf_cliente",
            field=models.CharField(max_length=11),
        ),
        migrations.AlterField(
            model_name="pedido",
            name="email_cliente",
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name="pedido",
            name="cep_cliente",
            field=models.CharField(max_length=9),
        ),
    ]

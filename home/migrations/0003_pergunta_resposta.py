from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_pergunta"),
    ]

    operations = [
        migrations.AddField(
            model_name="pergunta",
            name="resposta",
            field=models.TextField(blank=True, null=True),
        ),
    ]

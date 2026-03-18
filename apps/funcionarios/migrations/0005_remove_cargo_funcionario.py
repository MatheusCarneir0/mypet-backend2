"""
Reverse migration: remove CargoFuncionario model and revert
Funcionario.cargo field to max_length=20 with TextChoices.
"""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("funcionarios", "0004_seed_cargos"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CargoFuncionario",
        ),
        migrations.AlterField(
            model_name="funcionario",
            name="cargo",
            field=models.CharField(
                choices=[
                    ("ATENDENTE", "Atendente"),
                    ("TOSADOR", "Tosador"),
                    ("VETERINARIO", "Veterinário"),
                    ("GERENTE", "Gerente"),
                ],
                max_length=20,
                verbose_name="Cargo",
            ),
        ),
    ]

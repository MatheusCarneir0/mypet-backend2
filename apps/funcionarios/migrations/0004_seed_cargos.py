# Generated data migration to seed default cargos

from django.db import migrations


def seed_cargos(apps, schema_editor):
    CargoFuncionario = apps.get_model('funcionarios', 'CargoFuncionario')
    cargos = [
        ('ATENDENTE', 'Atendente', 'Responsável pelo atendimento ao cliente'),
        ('TOSADOR', 'Tosador', 'Responsável pela tosa dos pets'),
        ('VETERINARIO', 'Veterinário', 'Profissional de saúde animal'),
        ('GERENTE', 'Gerente', 'Responsável pela gestão da equipe'),
    ]
    for valor, nome_display, descricao in cargos:
        CargoFuncionario.objects.get_or_create(
            valor=valor,
            defaults={'nome_display': nome_display, 'descricao': descricao}
        )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("funcionarios", "0003_create_cargo_funcionario"),
    ]

    operations = [
        migrations.RunPython(seed_cargos, reverse_seed),
    ]

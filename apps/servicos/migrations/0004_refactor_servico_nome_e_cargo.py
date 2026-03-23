# apps/servicos/migrations/0004_refactor_servico_nome_e_cargo.py
"""
Migration manual: refatora o modelo Servico.
- Remove campo 'tipo' (TextChoices fixas)
- Remove campo 'duracao_medio_grande'
- Adiciona campo 'nome' (texto livre)
- Altera help_text do campo 'duracao_minutos'
- Cria modelo ServicoCargo (relacionamento servico <-> cargo)
"""
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("servicos", "0003_servico_duracao_medio_grande_and_more"),
    ]

    operations = [
        # 1. Adicionar 'nome' com valor padrão temporário (para não quebrar dados existentes)
        migrations.AddField(
            model_name="servico",
            name="nome",
            field=models.CharField(
                default="Serviço",
                help_text="Ex: Tosa Completa, Consulta Veterinária, Banho Terapêutico",
                max_length=100,
                verbose_name="Nome do Serviço",
            ),
            preserve_default=False,
        ),
        # 2. Remover campo 'tipo'
        migrations.RemoveField(
            model_name="servico",
            name="tipo",
        ),
        # 3. Remover campo 'duracao_medio_grande'
        migrations.RemoveField(
            model_name="servico",
            name="duracao_medio_grande",
        ),
        # 4. Alterar ordering e help_text de 'duracao_minutos'
        migrations.AlterField(
            model_name="servico",
            name="duracao_minutos",
            field=models.PositiveIntegerField(
                help_text="Duração média estimada do serviço em minutos",
                verbose_name="Duração em Minutos",
            ),
        ),
        # 5. Alterar ordering do Meta (de 'tipo' para 'nome')
        migrations.AlterModelOptions(
            name="servico",
            options={
                "ordering": ["nome"],
                "verbose_name": "Serviço",
                "verbose_name_plural": "Serviços",
            },
        ),
        # 6. Criar modelo ServicoCargo
        migrations.CreateModel(
            name="ServicoCargo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Data e hora de criação do registro",
                        verbose_name="Data de Criação",
                    ),
                ),
                (
                    "data_atualizacao",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Data e hora da última atualização",
                        verbose_name="Data de Atualização",
                    ),
                ),
                (
                    "ativo",
                    models.BooleanField(
                        default=True,
                        help_text="Indica se o registro está ativo",
                        verbose_name="Ativo",
                    ),
                ),
                (
                    "data_exclusao",
                    models.DateTimeField(
                        blank=True,
                        help_text="Data e hora da exclusão lógica",
                        null=True,
                        verbose_name="Data de Exclusão",
                    ),
                ),
                (
                    "cargo",
                    models.CharField(
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
                (
                    "servico",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cargos",
                        to="servicos.servico",
                        verbose_name="Serviço",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cargo do Serviço",
                "verbose_name_plural": "Cargos do Serviço",
                "db_table": "servicos_cargos",
                "ordering": ["servico", "cargo"],
                "unique_together": {("servico", "cargo")},
            },
        ),
    ]

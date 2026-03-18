import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.contrib.auth.models import Group
from apps.authentication.models import Usuario
from apps.clientes.models import Cliente
from apps.funcionarios.models import Funcionario


def ensure_groups():
    for name in ["ADMINISTRADOR", "FUNCIONARIO", "CLIENTE"]:
        Group.objects.get_or_create(name=name)


def ensure_admin():
    email = "admin@farmavet.com"
    password = "admin@123"
    user = Usuario.objects.filter(email=email).first()

    if not user:
        user = Usuario.objects.create_superuser(
            email=email,
            senha=password,
            nome="Administrador",
            telefone="88999999999",
        )
    else:
        user.nome = "Administrador"
        user.telefone = "88999999999"
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        user.groups.clear()
        user.groups.add(Group.objects.get(name="ADMINISTRADOR"))


def ensure_funcionario():
    email = "funcionario@farmavet.com"
    password = "func@123"
    user = Usuario.objects.filter(email=email).first()

    if not user:
        user = Usuario.objects.create_user(
            email=email,
            senha=password,
            nome="Funcionario Teste",
            telefone="88988888888",
            is_staff=True,
        )
    else:
        user.nome = "Funcionario Teste"
        user.telefone = "88988888888"
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()

    user.groups.clear()
    user.groups.add(Group.objects.get(name="FUNCIONARIO"))

    Funcionario.objects.update_or_create(
        usuario=user,
        defaults={
            "cargo": "ATENDENTE",
            "horario_trabalho": "Segunda a Sexta, 08:00-17:00",
            "ativo": True,
        },
    )


def ensure_cliente():
    email = "cliente@farmavet.com"
    password = "cliente@123"
    user = Usuario.objects.filter(email=email).first()

    if not user:
        user = Usuario.objects.create_user(
            email=email,
            senha=password,
            nome="Cliente Teste",
            telefone="88977777777",
        )
    else:
        user.nome = "Cliente Teste"
        user.telefone = "88977777777"
        user.is_active = True
        user.set_password(password)
        user.save()

    user.groups.clear()
    user.groups.add(Group.objects.get(name="CLIENTE"))

    Cliente.objects.update_or_create(
        usuario=user,
        defaults={
            "cpf": "123.456.789-00",
            "endereco": "Rua das Flores, 100",
            "cidade": "Boa Viagem",
            "estado": "CE",
            "cep": "63870-000",
            "ativo": True,
        },
    )


def main():
    ensure_groups()
    ensure_admin()
    ensure_funcionario()
    ensure_cliente()
    print("OK_USUARIOS_3_PERFIS")


if __name__ == "__main__":
    main()

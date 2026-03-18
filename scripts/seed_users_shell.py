"""
Script para criar 4 usuarios de teste no MyPet.
Rodar via: docker-compose exec web python manage.py shell < scripts/seed_users_shell.py
"""
from django.contrib.auth.models import Group
from apps.authentication.models import Usuario
from apps.clientes.models import Cliente

# Garantir que os grupos existam
grupo_admin, _ = Group.objects.get_or_create(name='ADMINISTRADOR')
grupo_func, _ = Group.objects.get_or_create(name='FUNCIONARIO')
grupo_cliente, _ = Group.objects.get_or_create(name='CLIENTE')

print("=" * 50)
print("CRIANDO USUARIOS DE TESTE")
print("=" * 50)

# 1. ADMINISTRADOR
email_admin = 'admin@farmavet.com'
if not Usuario.objects.filter(email=email_admin).exists():
    user_admin = Usuario.objects.create_superuser(
        email=email_admin,
        senha='Admin@123',
        nome='Administrador FarmaVet',
        telefone='(88) 99999-0001'
    )
    print(f"[OK] Administrador criado: {email_admin} / Admin@123")
else:
    user_admin = Usuario.objects.get(email=email_admin)
    user_admin.set_password('Admin@123')
    user_admin.is_staff = True
    user_admin.is_superuser = True
    user_admin.ativo = True
    user_admin.save()
    if not user_admin.groups.filter(name='ADMINISTRADOR').exists():
        user_admin.groups.add(grupo_admin)
    print(f"[OK] Administrador atualizado: {email_admin} / Admin@123")

# 2. FUNCIONARIO
email_func = 'funcionario@farmavet.com'
if not Usuario.objects.filter(email=email_func).exists():
    user_func = Usuario.objects.create_user(
        email=email_func,
        senha='Func@123',
        nome='Maria Funcionaria',
        telefone='(88) 99999-0002'
    )
    user_func.groups.add(grupo_func)
    print(f"[OK] Funcionario criado: {email_func} / Func@123")
else:
    user_func = Usuario.objects.get(email=email_func)
    user_func.set_password('Func@123')
    user_func.ativo = True
    user_func.save()
    if not user_func.groups.filter(name='FUNCIONARIO').exists():
        user_func.groups.add(grupo_func)
    print(f"[OK] Funcionario atualizado: {email_func} / Func@123")

# 3. CLIENTE 1
email_cli1 = 'joao@email.com'
if not Usuario.objects.filter(email=email_cli1).exists():
    user_cli1 = Usuario.objects.create_user(
        email=email_cli1,
        senha='Cliente@123',
        nome='Joao Silva',
        telefone='(88) 99999-0003'
    )
    user_cli1.groups.add(grupo_cliente)
    Cliente.objects.create(
        usuario=user_cli1,
        cpf='111.111.111-11',
        endereco='Rua das Flores, 100',
        cidade='Boa Viagem',
        estado='CE',
        cep='63870-000'
    )
    print(f"[OK] Cliente 1 criado: {email_cli1} / Cliente@123")
else:
    user_cli1 = Usuario.objects.get(email=email_cli1)
    user_cli1.set_password('Cliente@123')
    user_cli1.ativo = True
    user_cli1.save()
    if not user_cli1.groups.filter(name='CLIENTE').exists():
        user_cli1.groups.add(grupo_cliente)
    print(f"[OK] Cliente 1 atualizado: {email_cli1} / Cliente@123")

# 4. CLIENTE 2
email_cli2 = 'ana@email.com'
if not Usuario.objects.filter(email=email_cli2).exists():
    user_cli2 = Usuario.objects.create_user(
        email=email_cli2,
        senha='Cliente@123',
        nome='Ana Oliveira',
        telefone='(88) 99999-0004'
    )
    user_cli2.groups.add(grupo_cliente)
    Cliente.objects.create(
        usuario=user_cli2,
        cpf='222.222.222-22',
        endereco='Av. Principal, 200',
        cidade='Boa Viagem',
        estado='CE',
        cep='63870-001'
    )
    print(f"[OK] Cliente 2 criado: {email_cli2} / Cliente@123")
else:
    user_cli2 = Usuario.objects.get(email=email_cli2)
    user_cli2.set_password('Cliente@123')
    user_cli2.ativo = True
    user_cli2.save()
    if not user_cli2.groups.filter(name='CLIENTE').exists():
        user_cli2.groups.add(grupo_cliente)
    print(f"[OK] Cliente 2 atualizado: {email_cli2} / Cliente@123")

print()
print("=" * 50)
print("RESUMO DOS USUARIOS")
print("=" * 50)
print()
print("  ADMINISTRADOR:  admin@farmavet.com / Admin@123")
print("  FUNCIONARIO:    funcionario@farmavet.com / Func@123")
print("  CLIENTE 1:      joao@email.com / Cliente@123")
print("  CLIENTE 2:      ana@email.com / Cliente@123")
print()

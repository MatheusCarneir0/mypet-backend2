from apps.clientes.models import Cliente
for c in Cliente.objects.all():
    print(f"Cliente ID: {c.id} | Usuario ID: {c.usuario.id} | Email: {c.usuario.email}")

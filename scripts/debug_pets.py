from apps.pets.models import Pet
for p in Pet.objects.all():
    cliente_info = f"Cliente ID: {p.cliente.id}, Email: {p.cliente.usuario.email}" if p.cliente else "SEM CLIENTE"
    print(f"Pet: {p.nome} (id={p.id}) | {cliente_info} | Especie: {p.especie} | Ativo: {p.ativo}")

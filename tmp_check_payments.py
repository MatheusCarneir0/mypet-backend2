import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.pagamentos.models import FormaPagamento

count = FormaPagamento.objects.count()
print(f"TOTAL_FORMAS_PAGAMENTO: {count}")
for fp in FormaPagamento.objects.all():
    print(f"ID: {fp.id}, Nome: {fp.nome}, Ativo: {fp.ativo}")

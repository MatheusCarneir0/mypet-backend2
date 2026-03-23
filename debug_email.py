import os
import django
import sys

# Setup Django
sys.path.append('c:/Users/Matheus/Documents/MyPet_v5/backend - Copia')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from apps.authentication.models import Usuario

email_teste = 'matheusthayna082@gmail.com'

print(f"--- Diagnóstico de E-mail ---")
print(f"Tentando encontrar usuário: {email_teste}")
user = Usuario.objects.filter(email=email_teste).first()

if not user:
    print(f"ERRO: Usuário '{email_teste}' NÃO encontrado no banco de dados!")
    print("Usuários cadastrados no momento:")
    for u in Usuario.objects.all()[:5]:
        print(f" - {u.email}")
else:
    print(f"Sucesso: Usuário encontrado: {user.nome}")
    print(f"Tentando enviar e-mail via {settings.EMAIL_HOST}...")
    try:
        res = send_mail(
            subject='Teste de Diagnóstico MyPet',
            message='Se você recebeu isso, o SMTP do Gmail está funcionando!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_teste],
            fail_silently=False,
        )
        print(f"Resultado do send_mail: {res}")
        if res:
            print("E-mail enviado com sucesso para o servidor do Google!")
    except Exception as e:
        print(f"ERRO AO ENVIAR E-MAIL: {type(e).__name__}: {str(e)}")

#!/usr/bin/env python
"""
Script para criar ou atualizar usuário administrador.
Garante que admin@mypet.com tenha todas as permissões necessárias.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.authentication.models import Usuario


def criar_admin():
    """
    Cria ou atualiza o usuário administrador.
    """
    email = 'admin@mypet.com'
    senha = 'admin123'  # Altere em produção!
    
    try:
        usuario, created = Usuario.objects.get_or_create(
            email=email,
            defaults={
                'nome': 'Administrador',
                'telefone': '(00) 00000-0000',
                'tipo_usuario': Usuario.TipoUsuario.ADMINISTRADOR,
                'is_staff': True,
                'is_superuser': True,
                'ativo': True
            }
        )
        
        if not created:
            # Atualizar usuário existente
            usuario.nome = 'Administrador'
            usuario.tipo_usuario = Usuario.TipoUsuario.ADMINISTRADOR
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.ativo = True
            usuario.set_password(senha)
            usuario.save()
            print(f'✅ Usuário {email} atualizado com sucesso!')
        else:
            usuario.set_password(senha)
            usuario.save()
            print(f'✅ Usuário {email} criado com sucesso!')
        
        print(f'\n📧 Email: {email}')
        print(f'🔑 Senha: {senha}')
        print(f'\n⚠️  ATENÇÃO: Altere a senha após o primeiro login!')
        
    except Exception as e:
        print(f'❌ Erro ao criar usuário: {str(e)}')
        sys.exit(1)


if __name__ == '__main__':
    criar_admin()


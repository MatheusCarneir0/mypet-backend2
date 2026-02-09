# Generated migration for data migration: tipo_usuario to Groups

from django.db import migrations


def migrate_tipo_usuario_to_groups(apps, schema_editor):
    """
    Migra dados existentes de tipo_usuario para Django Groups.
    Para cada usuário com tipo_usuario definido, adiciona ao grupo correspondente.
    """
    Usuario = apps.get_model('authentication', 'Usuario')
    Group = apps.get_model('auth', 'Group')
    
    # Criar grupos se não existirem
    cliente_group, _ = Group.objects.get_or_create(name='CLIENTE')
    funcionario_group, _ = Group.objects.get_or_create(name='FUNCIONARIO')
    admin_group, _ = Group.objects.get_or_create(name='ADMINISTRADOR')
    
    # Migrar usuários existentes
    for usuario in Usuario.objects.all():
        if hasattr(usuario, 'tipo_usuario'):
            if usuario.tipo_usuario == 'CLIENTE':
                usuario.groups.add(cliente_group)
            elif usuario.tipo_usuario == 'FUNCIONARIO':
                usuario.groups.add(funcionario_group)
            elif usuario.tipo_usuario == 'ADMINISTRADOR':
                usuario.groups.add(admin_group)


def reverse_migration(apps, schema_editor):
    """
    Migração reversa: remove usuários de todos os grupos.
    ATENÇÃO: Isso não restaura o campo tipo_usuario, apenas limpa os grupos.
    """
    Usuario = apps.get_model('authentication', 'Usuario')
    
    for usuario in Usuario.objects.all():
        usuario.groups.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(migrate_tipo_usuario_to_groups, reverse_migration),
    ]

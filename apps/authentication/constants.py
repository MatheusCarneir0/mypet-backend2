# apps/authentication/constants.py

class UserGroups:
    """
    Constantes para os nomes dos grupos de usuários.
    Evita o uso de 'magic strings' pelo código.
    """
    CLIENTE = 'CLIENTE'
    FUNCIONARIO = 'FUNCIONARIO'
    ADMINISTRADOR = 'ADMINISTRADOR'
    
    @classmethod
    def choices(cls):
        return [
            (cls.CLIENTE, 'Cliente'),
            (cls.FUNCIONARIO, 'Funcionário'),
            (cls.ADMINISTRADOR, 'Administrador'),
        ]

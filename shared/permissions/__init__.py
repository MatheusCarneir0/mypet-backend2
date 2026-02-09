# shared/permissions/__init__.py
"""
Permissões customizadas do projeto MyPet.
"""
from .groups import (
    IsCliente,
    IsFuncionario,
    IsAdministrador,
    IsFuncionarioOrAdmin,
    IsClienteOwner,
    ReadOnlyForCliente,
)

__all__ = [
    'IsCliente',
    'IsFuncionario',
    'IsAdministrador',
    'IsFuncionarioOrAdmin',
    'IsClienteOwner',
    'ReadOnlyForCliente',
]

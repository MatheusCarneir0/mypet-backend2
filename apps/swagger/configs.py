from drf_spectacular.utils import extend_schema

def swagger_setup(tag, description=""):
    """
    Helper para organizar o Swagger por módulos.
    """
    return extend_schema_view(
        list=extend_schema(tags=[tag], summary=f"Listar {tag}"),
        create=extend_schema(tags=[tag], summary=f"Criar {tag}"),
        retrieve=extend_schema(tags=[tag], summary=f"Detalhar {tag}"),
        update=extend_schema(tags=[tag], summary=f"Atualizar {tag}"),
        partial_update=extend_schema(tags=[tag], summary=f"Atualizar Parcial {tag}"),
        destroy=extend_schema(tags=[tag], summary=f"Remover {tag}"),
    )

# Importamos isso para poder usar como decorator nas Views
from drf_spectacular.utils import extend_schema_view
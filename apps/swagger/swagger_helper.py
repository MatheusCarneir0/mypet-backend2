 
from rest_framework import serializers

class MetaPaginationSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)

_ENVELOPE_SEQ = 0

def envelop(data, paginated=False):
    global _ENVELOPE_SEQ
    _ENVELOPE_SEQ += 1
    
    # Suporta classe ou instância
    data_field = data() if isinstance(data, type) else data
    base_name = data.__name__ if isinstance(data, type) else data.__class__.__name__
    
    name = f"{base_name}Envelope_{_ENVELOPE_SEQ}"

    attrs = {
        "success": serializers.BooleanField(default=True),
        "message": serializers.CharField(default="Operação realizada com sucesso"),
        "data": data_field,
    }
    if paginated:
        attrs["meta"] = MetaPaginationSerializer()

    return type(name, (serializers.Serializer,), attrs)
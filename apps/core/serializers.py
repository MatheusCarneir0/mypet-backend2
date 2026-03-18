from rest_framework import serializers
from .models import HorarioTrabalho

class HorarioTrabalhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioTrabalho
        fields = '__all__'

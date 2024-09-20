from rest_framework import serializers
from .models import SubmitFile

class SubmitFileSerializer(serializers.ModelSerializer):
    class Meta:
        model=SubmitFile
        fields='__all__'
from rest_framework import serializers
from .models import Upload, EquipmentData

class EquipmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentData
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature']

class UploadSerializer(serializers.ModelSerializer):
    equipment_data = EquipmentDataSerializer(many=True, read_only=True)

    class Meta:
        model = Upload
        fields = ['id', 'file', 'uploaded_at', 'equipment_data']
        read_only_fields = ['uploaded_at', 'equipment_data']

class UploadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'file', 'uploaded_at']

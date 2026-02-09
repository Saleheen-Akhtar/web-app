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
        fields = ['id', 'file', 'original_filename', 'uploaded_at', 'equipment_data']
        read_only_fields = ['uploaded_at', 'equipment_data', 'original_filename']

class UploadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ['id', 'file', 'original_filename', 'uploaded_at']

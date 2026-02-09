import pandas as pd
from django.db import transaction
from django.http import HttpResponse, Http404
from django.db.models import Avg, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

from .models import Upload, EquipmentData
from .serializers import UploadSerializer, UploadListSerializer, EquipmentDataSerializer

class UploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_serializer = UploadSerializer(data=request.data)
        if file_serializer.is_valid():
            upload_instance = file_serializer.save()

            try:
                # Parse CSV
                df = pd.read_csv(upload_instance.file.path)

                # Check required columns
                required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
                if not all(col in df.columns for col in required_columns):
                    upload_instance.delete()
                    return Response({"error": f"Missing required columns. Expected: {required_columns}"}, status=status.HTTP_400_BAD_REQUEST)

                # Create EquipmentData objects
                equipment_list = []
                for _, row in df.iterrows():
                    equipment_list.append(EquipmentData(
                        upload=upload_instance,
                        equipment_name=row['Equipment Name'],
                        equipment_type=row['Type'],
                        flowrate=row['Flowrate'],
                        pressure=row['Pressure'],
                        temperature=row['Temperature']
                    ))

                with transaction.atomic():
                    EquipmentData.objects.bulk_create(equipment_list)

                return Response(file_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                upload_instance.delete()
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadListView(generics.ListAPIView):
    queryset = Upload.objects.all().order_by('-uploaded_at')
    serializer_class = UploadListSerializer

class DashboardView(APIView):
    def get(self, request, upload_id=None):
        if upload_id:
            try:
                upload = Upload.objects.get(id=upload_id)
            except Upload.DoesNotExist:
                return Response({"error": "Upload not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            upload = Upload.objects.order_by('-uploaded_at').first()
            if not upload:
                return Response({"error": "No uploads found"}, status=status.HTTP_404_NOT_FOUND)

        data = EquipmentData.objects.filter(upload=upload)

        # Calculate statistics
        count = data.count()
        avg_flowrate = data.aggregate(Avg('flowrate'))['flowrate__avg']
        avg_pressure = data.aggregate(Avg('pressure'))['pressure__avg']
        avg_temperature = data.aggregate(Avg('temperature'))['temperature__avg']

        # Handle None values if no data
        avg_flowrate = avg_flowrate if avg_flowrate is not None else 0
        avg_pressure = avg_pressure if avg_pressure is not None else 0
        avg_temperature = avg_temperature if avg_temperature is not None else 0

        type_distribution = list(data.values('equipment_type').annotate(count=Count('equipment_type')))

        raw_data = EquipmentDataSerializer(data, many=True).data

        response_data = {
            "upload_id": upload.id,
            "uploaded_at": upload.uploaded_at,
            "filename": upload.file.name,
            "summary": {
                "count": count,
                "avg_flowrate": avg_flowrate,
                "avg_pressure": avg_pressure,
                "avg_temperature": avg_temperature,
                "type_distribution": type_distribution
            },
            "data": raw_data
        }

        return Response(response_data)

class PDFReportView(APIView):
    def get(self, request, upload_id):
        try:
            upload = Upload.objects.get(id=upload_id)
        except Upload.DoesNotExist:
            raise Http404("Upload not found")

        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Calculate stats (reusing logic or calling utility function would be better, but duplicating for simplicity here)
        data = EquipmentData.objects.filter(upload=upload)
        count = data.count()
        avg_flowrate = data.aggregate(Avg('flowrate'))['flowrate__avg']
        avg_pressure = data.aggregate(Avg('pressure'))['pressure__avg']
        avg_temperature = data.aggregate(Avg('temperature'))['temperature__avg']
        type_distribution = list(data.values('equipment_type').annotate(count=Count('equipment_type')))

        # Draw things on the PDF.
        y = height - 50
        p.drawString(100, y, f"Report for Upload {upload.id} ({upload.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')})")
        y -= 30
        p.drawString(100, y, "Summary Statistics")
        y -= 20
        p.drawString(120, y, f"Total Equipment Count: {count}")
        y -= 20
        p.drawString(120, y, f"Average Flowrate: {avg_flowrate:.2f}" if avg_flowrate else "Average Flowrate: N/A")
        y -= 20
        p.drawString(120, y, f"Average Pressure: {avg_pressure:.2f}" if avg_pressure else "Average Pressure: N/A")
        y -= 20
        p.drawString(120, y, f"Average Temperature: {avg_temperature:.2f}" if avg_temperature else "Average Temperature: N/A")

        y -= 40
        p.drawString(100, y, "Equipment Type Distribution")
        y -= 20
        for item in type_distribution:
            p.drawString(120, y, f"{item['equipment_type']}: {item['count']}")
            y -= 20

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

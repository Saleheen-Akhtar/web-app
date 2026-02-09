from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from .models import Upload, EquipmentData

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Register a user
        self.username = "testuser"
        self.password = "password123"
        self.email = "test@example.com"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        # Login (get token)
        response = self.client.post('/api/token-auth/', {'username': self.username, 'password': self.password}, format='json')
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_upload_csv(self):
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nEq1,TypeA,100,50,25\nEq2,TypeB,200,60,30"
        csv_file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")

        response = self.client.post('/api/upload/', {'file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Upload.objects.count(), 1)
        self.assertEqual(EquipmentData.objects.count(), 2)

    def test_dashboard(self):
        # Create upload first
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nEq1,TypeA,100,50,25"
        csv_file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")
        self.client.post('/api/upload/', {'file': csv_file}, format='multipart')
        upload = Upload.objects.first()

        response = self.client.get(f'/api/dashboard/{upload.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary']['count'], 1)

    def test_history(self):
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nEq1,TypeA,100,50,25"
        csv_file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")
        self.client.post('/api/upload/', {'file': csv_file}, format='multipart')

        response = self.client.get('/api/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_pdf_report(self):
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nEq1,TypeA,100,50,25"
        csv_file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")
        self.client.post('/api/upload/', {'file': csv_file}, format='multipart')
        upload = Upload.objects.first()

        response = self.client.get(f'/api/report/{upload.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_limit_uploads(self):
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nEq1,TypeA,100,50,25"
        for i in range(7):
            csv_file = SimpleUploadedFile(f"test_data_{i}.csv", csv_content, content_type="text/csv")
            self.client.post('/api/upload/', {'file': csv_file}, format='multipart')

        self.assertEqual(Upload.objects.count(), 5)

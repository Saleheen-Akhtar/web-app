from django.urls import path
from .views import UploadView, UploadListView, DashboardView, PDFReportView

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('history/', UploadListView.as_view(), name='history'),
    path('dashboard/', DashboardView.as_view(), name='dashboard_latest'),
    path('dashboard/<int:upload_id>/', DashboardView.as_view(), name='dashboard_specific'),
    path('report/<int:upload_id>/', PDFReportView.as_view(), name='pdf_report'),
]

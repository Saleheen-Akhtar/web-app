from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os

class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id} at {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']  # Newest first

class EquipmentData(models.Model):
    upload = models.ForeignKey(Upload, related_name='equipment_data', on_delete=models.CASCADE)
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"

# Signal to keep only last 5 uploads
@receiver(post_save, sender=Upload)
def limit_uploads(sender, instance, created, **kwargs):
    if created:
        uploads = Upload.objects.all().order_by('-uploaded_at')
        if uploads.count() > 5:
            # Get the uploads to delete (everything after the 5th one)
            uploads_to_delete = uploads[5:]
            for upload in uploads_to_delete:
                upload.delete()

# Signal to delete file when Upload model is deleted
@receiver(post_delete, sender=Upload)
def delete_file_on_upload_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

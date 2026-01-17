from django.db import models
import uuid
from django.utils import timezone

class ScanSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.CharField(max_length=255)
    start_time = models.DateTimeField(default=timezone.now)
    is_complete = models.BooleanField(default=False)
    # NEU: Speichert den Fortschritt des Balkens
    completed_steps = models.IntegerField(default=0)
    
    hostname = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    os_type = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.target} - {self.id}"

class Finding(models.Model):
    session = models.ForeignKey(ScanSession, on_delete=models.CASCADE, related_name='findings')
    category = models.CharField(max_length=50)
    value = models.CharField(max_length=500)
    severity = models.CharField(max_length=20, default='Info')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'category', 'value')

class AvailableOperation(models.Model):
    session = models.ForeignKey(ScanSession, on_delete=models.CASCADE, related_name='operations')
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, default='External')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

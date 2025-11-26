from django.db import models
from django.utils import timezone
import uuid

class AnalyzedTask(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    task_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    score = models.FloatField()
    urgency = models.FloatField()
    importance = models.FloatField()
    effort = models.FloatField()
    dependency = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
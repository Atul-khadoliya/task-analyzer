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
    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']


class GlobalSettings(models.Model):
    # Default weights
    default_urgency = models.FloatField(default=0.4)
    default_importance = models.FloatField(default=0.3)
    default_effort = models.FloatField(default=0.2)
    default_dependency = models.FloatField(default=0.1)

    # Learned weights
    weight_urgency = models.FloatField(default=0.4)
    weight_importance = models.FloatField(default=0.3)
    weight_effort = models.FloatField(default=0.2)
    weight_dependency = models.FloatField(default=0.1)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global Weight Settings"

    @staticmethod
    def get():
        obj, created = GlobalSettings.objects.get_or_create(id=1)
        return obj


class Feedback(models.Model):
    task_id = models.CharField(max_length=100)
    was_helpful = models.BooleanField()

    urgency = models.FloatField(default=0)
    importance = models.FloatField(default=0)
    effort = models.FloatField(default=0)
    dependency = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on {self.task_id}"

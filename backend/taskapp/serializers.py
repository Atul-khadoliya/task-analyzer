from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    title = serializers.CharField(required=True, allow_blank=False)
    due_date = serializers.DateField(required=True)  # VALIDATES DATE
    estimated_hours = serializers.IntegerField(min_value=0)  # NO NEGATIVE HOURS
    importance = serializers.IntegerField(min_value=1, max_value=10)  # 1–10 ONLY
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )


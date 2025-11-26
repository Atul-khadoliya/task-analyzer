from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, allow_null=True)
    dependencies = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

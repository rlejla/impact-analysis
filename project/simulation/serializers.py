from rest_framework import serializers

class GuidelineConditionSerializer(serializers.Serializer):
    field = serializers.CharField()
    operator = serializers.CharField()
    value = serializers.JSONField()

class GuidelineConditionsSerializer(serializers.Serializer):
    logic = serializers.CharField(default="all")
    conditions = GuidelineConditionSerializer(many=True)

class GuidelineSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True),
    name = serializers.CharField()
    conditions = GuidelineConditionsSerializer()
    action = serializers.CharField()
    priority = serializers.IntegerField()
    effective_date = serializers.DateField()
    version = serializers.IntegerField()
    coverage_types = serializers.ListField(child=serializers.CharField())
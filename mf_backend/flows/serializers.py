# flow/serializers.py
from rest_framework import serializers
from .models import Flow, FlowStep

class FlowStepSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = FlowStep
        fields = ('id', 'step_order', 'step_description')

class FlowSerializer(serializers.ModelSerializer):
    flow_steps = FlowStepSerializer(many=True)

    class Meta:
        model = Flow
        fields = ('id', 'flow_id', 'flow_description', 'category', 'is_active', 'expected_duration',
                  'created_at', 'modified_at', 'created_by', 'modified_by', 'flow_steps')
        read_only_fields = ('created_at', 'modified_at')

    def create(self, validated_data):
        steps_data = validated_data.pop('flow_steps', [])
        flow = Flow.objects.create(**validated_data)
        for i, step in enumerate(steps_data, start=1):
            FlowStep.objects.create(flow=flow, step_order=step.get('step_order', i), step_description=step['step_description'])
        return flow

    def update(self, instance, validated_data):
        steps_data = validated_data.pop('flow_steps', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if steps_data is not None:
            # Replace steps: simple approach - delete existing and recreate.
            instance.flow_steps.all().delete()
            for i, step in enumerate(steps_data, start=1):
                FlowStep.objects.create(flow=instance, step_order=step.get('step_order', i), step_description=step['step_description'])

        return instance
    
class FlowStepTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowStep
        fields = ['step_order', 'step_description']


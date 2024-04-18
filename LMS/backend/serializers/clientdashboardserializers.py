from rest_framework import serializers
from backend.models.allmodels import CourseEnrollment, CourseCompletionStatusPerUser

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'user_id', 'course_id', 'active']

    def validate(self, data):
        # Add custom validation logic here
        # For example, you can check if 'active' is a boolean value
        active = data.get('active')
        if active is not None and not isinstance(active, bool):
            raise serializers.ValidationError("Active must be a boolean value")
        return data


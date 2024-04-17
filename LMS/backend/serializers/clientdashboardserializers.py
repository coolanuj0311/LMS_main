from rest_framework import serializers
from backend.models.allmodels import CourseEnrollment, CourseCompletionStatusPerUser

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ['course_id', 'user_id', 'active']

class CourseCompletionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletionStatusPerUser
        fields = ['enrolled_user_id', 'status', 'active']

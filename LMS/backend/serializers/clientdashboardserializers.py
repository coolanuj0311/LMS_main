from rest_framework import serializers
from backend.models.allmodels import CourseEnrollment, CourseCompletionStatusPerUser

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'user_id', 'course_id', 'active']

class CourseCompletionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletionStatusPerUser
        fields = ['id', 'enrolled_user_id', 'status', 'active']

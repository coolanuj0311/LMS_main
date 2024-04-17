# serializers.py

from rest_framework import serializers
from backend.models.allmodels import CourseCompletionStatusPerUser
from rest_framework import serializers
from backend.models.allmodels import QuizAttemptHistory, QuizScore
from rest_framework import serializers
from backend.models.allmodels import QuizScore


class CourseCompletionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletionStatusPerUser
        fields = ['enrolled_user_id', 'course_id', 'status', 'created_at']




class QuizScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizScore
        fields = ['course_id', 'enrolled_user_id', 'total_score_per_course']

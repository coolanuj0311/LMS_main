from rest_framework import serializers
from backend.models.allmodels import CourseCompletionStatusPerUser
from rest_framework import serializers
from backend.models.allmodels import QuizAttemptHistory, QuizScore


class CourseCompletionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletionStatusPerUser
        fields = ['enrolled_user_id', 'course_id', 'status', 'created_at']


class QuizAttemptHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttemptHistory
        fields = ['course_id', 'enrolled_user_id', 'quiz_id', 'complete']

class QuizScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizScore
        fields = ['course_id', 'enrolled_user_id', 'completed_quiz_count']

from rest_framework import serializers
from backend.models.allmodels import CourseCompletionStatusPerUser
from backend.models.allmodels import QuizScore

class CourseCompletionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCompletionStatusPerUser
        fields = ['enrolled_user_id', 'course_id', 'status', 'created_at']

    def validate(self, data):
        # Add custom validation logic here
        # For example, you can check if 'status' is a valid value
        status = data.get('status')
        if status not in ['completed','in_progress','not_started']:
            raise serializers.ValidationError("Status must be 'completed' or 'in_progress'or'not_started'")
        return data

class QuizScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizScore
        fields = ['enrolled_user_id', 'course_id', 'total_quizzes_per_course', 'completed_quiz_count', 'total_score_per_course', 'created_at', 'updated_at', 'active']

    def validate(self, data):
        # Add custom validation logic here
        # For example, you can check if 'total_quizzes_per_course' is a positive integer
        total_quizzes_per_course = data.get('total_quizzes_per_course')
        if total_quizzes_per_course is not None and total_quizzes_per_course <= 0:
            raise serializers.ValidationError("Total quizzes must be a positive integer")
        return data

from rest_framework import  status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.serializers.scoreserializers import CourseCompletionStatusSerializer
from core.custom_permissions import ClientPermission
from core.custom_mixins import ClientMixin
from backend.models.allmodels import (
    CourseCompletionStatusPerUser,
    CourseEnrollment,
    QuizScore,
)
from backend.serializers.clientdashboardserializers import CourseEnrollmentSerializer


class DisplayClientCourseProgressView(APIView):

    permission_classes = [ClientPermission]
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')

            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            course_enrollments = CourseEnrollment.objects.filter(user_id=user_id, active=True)

            if not course_enrollments:
                return Response({'message': 'No active enrollment found for the user'}, status=status.HTTP_404_NOT_FOUND)

            progress_data = []
            for enrollment in course_enrollments:
                quiz_score = QuizScore.objects.filter(course_id=enrollment.course_id, enrolled_user_id=user_id).first()
                if quiz_score:
                   
                    progress_percentage = 0
                    total_quiz_count = quiz_score.total_quizzes_per_course
                    completed_quiz_count = quiz_score.completed_quiz_count

                    if total_quiz_count == completed_quiz_count:
                        completion_status = "completed"
                  
                    elif completed_quiz_count == 0:
                        completion_status ="not_started"
                    else:
                        completion_status = "in_progress"
                     
                    if quiz_score.total_quizzes_per_course > 0:
                        progress_percentage = (quiz_score.completed_quiz_count / quiz_score.total_quizzes_per_course) * 100
                    
                    progress_data.append({
                        'course_id': enrollment.course_id,
                        'course_name': enrollment.course.title,
                        'completed_quiz_count': quiz_score.completed_quiz_count,
                        'total_quizzes_per_course': quiz_score.total_quizzes_per_course,
                        'progress_percentage': progress_percentage,
                        'completion_status': completion_status
                    })

            serializer = CourseEnrollmentSerializer(course_enrollments, many=True)
            return Response({'progress': progress_data, 'enrollments': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CountCoursesStatusView(APIView):
    """
    GET request to count the number of active enrollments and course completion status for a user.
    """
   
    permission_classes = [ClientPermission]

    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Count active enrollments for the user
            active_enrollments_count = CourseEnrollment.objects.filter(user_id=user_id, active=True).count()

            # Count completed, in-progress, and not started courses
            completed_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, status='completed', active=True).count()
            in_progress_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, status='in_progress', active=True).count()
            not_started_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, status='not_started', active=True).count()

            return Response({
                'active_enrollments_count': active_enrollments_count,
                'completed_courses_count': completed_courses_count,
                'in_progress_courses_count': in_progress_courses_count,
                'not_started_courses_count': not_started_courses_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



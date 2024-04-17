from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status

from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max

from backend.serializers.scoreserializers import CourseCompletionStatusSerializer
from core.custom_permissions import ClientAdminPermission
from core.custom_mixins import ClientAdminMixin

from backend.models.allmodels import (
    CourseCompletionStatusPerUser,
    CourseStructure,
    QuizAttemptHistory,
    QuizScore,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.custom_permissions import ClientAdminPermission
from core.custom_mixins import ClientAdminMixin
from backend.models.allmodels import CourseCompletionStatusPerUser



class CreateCourseCompletionStatusPerUserView(ClientAdminMixin, APIView):
    """
    allowed for client admin
    POST request
    triggered after course enrollment records creation, similar to that one.
    in request body:
        list of course_id =[..., ..., ..., ...]
        list of user_id =[..., ..., ..., ...]
        each course in list will be mapped for all users in list
    while creating instance:
        enrolled_user = request body
        course = request body
        status = (default='not started')
        created_at = (auto_now_add=True)
    """
    permission_classes = [ClientAdminPermission]

    def post(self, request):
        try:
            course_ids = request.data.get('course_id', [])
            user_ids = request.data.get('user_id', [])

            if not course_ids or not user_ids:
                return Response({'error': 'course_id and user_id lists are required'}, status=status.HTTP_400_BAD_REQUEST)

            if not all(isinstance(course_id, int) for course_id in course_ids):
                return Response({'error': 'Invalid course_id format'}, status=status.HTTP_400_BAD_REQUEST)
            if not all(isinstance(user_id, int) for user_id in user_ids):
                return Response({'error': 'Invalid user_id format'}, status=status.HTTP_400_BAD_REQUEST)

            course_completion_statuses = []
            for course_id in course_ids:
                for user_id in user_ids:
                    if not CourseCompletionStatusPerUser.objects.filter(Q(course_id=course_id) & Q(enrolled_user_id=user_id)).exists():
                        course_completion_status = CourseCompletionStatusPerUser(
                            enrolled_user_id=user_id,
                            course_id=course_id,
                            status="not_started"
                        )
                        course_completion_statuses.append(course_completion_status)

            # Serialize the data
            serializer = CourseCompletionStatusSerializer(data=course_completion_statuses, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Course completion statuses created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    
class UpdateCompleteQuizCountView(ClientAdminMixin, APIView):
    """
    POST request triggered when quiz attempt history for that course, that user have completed = true,
    if set of quiz, course, user doesn't already have completed = true in table
    while updating instance:
        completed_quiz_count = count of distinct completed quizzes
    """
    permission_classes = [ClientAdminPermission]

    def post(self, request):
        try:
            # Check if the user has client admin privileges
            # if not self.has_client_admin_privileges(request):
            #     return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)

            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Count distinct completed quizzes for the user and course
            completed_quizzes_count = QuizAttemptHistory.objects.filter(course_id=course_id, enrolled_user_id=user_id, complete=True).values('quiz_id').distinct().count()

            # Update completed_quiz_count for the corresponding record
            quiz_score, created = QuizScore.objects.get_or_create(
                course_id=course_id,
                enrolled_user_id=user_id,
                defaults={'completed_quiz_count': 0}
            )
            quiz_score.completed_quiz_count = completed_quizzes_count
            quiz_score.save()

            return Response({'message': 'Completed quiz count updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        

class CreateQuizScoreView(ClientAdminMixin,APIView):
    """
    allowed for client admin
    POST request
    triggered after course enrollment records creation, similar to that one.
    in request body:
        list of course_id =[..., ..., ..., ...]
        list of user_id =[..., ..., ..., ...]
        each course in list will be mapped for all users in list
    while creating instance:
        enrolled_user = request body
        course = request body
        total_quizzes_per_course = calculate in view for course by counting active quizzes in it
        completed_quiz_count = by default 0
        total_score_per_course = (default=0)
    """
    permission_classes = [ClientAdminPermission]
    def post(self, request):
        try:
            # Check if the user has client admin privileges
            # if not self.has_client_admin_privileges(request):
            #     return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_ids = request.data.get('course_id', [])
            user_ids = request.data.get('user_id', [])

            # Validate request data
            if not course_ids or not user_ids:
                return Response({'error': 'course_id and user_id lists are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create quiz score records
            quiz_scores = []
            for course_id in course_ids:
                # Calculate total quizzes for the course
                total_quizzes_per_course = self.get_total_quizzes_per_course(course_id)

                for user_id in user_ids:
                    # Check if QuizScore instance already exists for this user and course
                    existing_score = QuizScore.objects.filter(course_id=course_id, enrolled_user_id=user_id).first()

                    if existing_score:
                        continue  # Skip creation if QuizScore instance already exists

                    # Create new QuizScore instance
                    quiz_score = QuizScore(
                        enrolled_user_id=user_id,
                        course_id=course_id,
                        total_quizzes_per_course=total_quizzes_per_course,
                        completed_quiz_count=0,
                        total_score_per_course=0,
                        created_at=timezone.now(),
                        updated_at=timezone.now(),
                        active=True
                    )
                    quiz_scores.append(quiz_score)

            # Save quiz score records to the database
            QuizScore.objects.bulk_create(quiz_scores)

            return Response({'message': 'Quiz scores created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_total_quizzes_per_course(self, course_id):
        try:
        # Count the number of quizzes associated with the given course_id
            total_quizzes = CourseStructure.objects.filter(course_id=course_id, content_type='quiz', active=True).count()
            return total_quizzes
        except Exception as e:
        # Handle exceptions if any
          return 0  # Return 0 in case of error


class UpdateTotalScorePerCourseView(ClientAdminMixin,APIView):
    """
    POST request
    triggered when quiz attempt history for that course, that user have completed = true 
    while updating instance:
        total_score_per_course -> calculate for it 
        score=current_score/question_list_order.split().count()
    """
    permission_classes = [ClientAdminPermission] #IsAuthenticated, 

    def post(self, request):
        try:
            # Check if the user has client admin privileges
            # if not self.has_client_admin_privileges(request):
            #     return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get unique instances of completed quizzes for the user and course
            
           

            last_attempted_quizzes = (
                QuizAttemptHistory.objects.filter(course_id=course_id, enrolled_user_id=user_id, complete=True)
                .values('quiz_id')
                .annotate(last_attempt=Max('created_at'))
                .order_by('-last_attempt')
            )

            unique_quizzes = QuizAttemptHistory.objects.filter(
                course_id=course_id,
                enrolled_user_id=user_id,
                complete=True,
                created_at__in=[quiz['last_attempt'] for quiz in last_attempted_quizzes]
            )

            # Calculate total score for the user and course
            total_score = 0
            for quiz_attempt in unique_quizzes:
                total_score += (quiz_attempt.current_score / (len(quiz_attempt.question_list_order.split(','))-1))


            # Get total quizzes for the course
            total_quizzes = QuizScore.objects.get(course_id=course_id, enrolled_user_id=user_id).total_quizzes_per_course
           

            # Calculate average score
            if total_quizzes > 0:
                average_score = (total_score / total_quizzes) * 100
            else:
                average_score = 0

            # Update total_score_per_course for the corresponding record
            quiz_score, created = QuizScore.objects.get_or_create(course_id=course_id, enrolled_user_id=user_id, defaults={'total_score_per_course': 0})
            quiz_score.total_score_per_course = average_score
            quiz_score.save()

            return Response({'message': 'Total score per course updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCourseCompletionStatusPerUserView(ClientAdminMixin,APIView):
    """
    POST request
    triggers when 
    total_quizzes_per_course = completed_quiz_count in quiz score for that user in request
    if total_quizzes_per_course == completed_quiz_count:
        completion_status=True and in_progress_status =False
    if total_quizzes_per_course > completed_quiz_count:
        completion_status=False and in_progress_status =True
        
    """
    permission_classes = [ClientAdminPermission]
    @transaction.atomic
    def post(self, request):
        
        try:
           
            # # Check if the user has client admin privileges
            # if not self.has_client_admin_privileges(request):
            #     return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve or create CourseCompletionStatus record
            course_completion_status, created = CourseCompletionStatusPerUser.objects.get_or_create(
                course_id=course_id, enrolled_user_id=user_id
            )

            # Retrieve quiz score record for the user and course
            quiz_score = get_object_or_404(QuizScore, course_id=course_id, enrolled_user_id=user_id)

            # Update completion status
            if quiz_score.total_quizzes_per_course == quiz_score.completed_quiz_count:
                course_completion_status.status = "completed"
                
            elif quiz_score.total_quizzes_per_course > quiz_score.completed_quiz_count:
                course_completion_status.status = "in_progress"
            else:
                course_completion_status.status = "not_started"

               

            # Save the updated CourseCompletionStatus record
            course_completion_status.save()

            return Response({'message': 'Course completion status updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, QuizScore.DoesNotExist):
                return Response({'error': 'Quiz score record not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



import json
from django.views import View
import pandas as pd
import requests
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Max
#custom_authentication in main model is "core"
# from core.custom_mixins import (
from core.custom_mixins import ClientAdminMixin, ClientMixin, SuperAdminMixin
#exam in main model "backend"
# from backend.models.allmodels import(
from exam.models.allmodels import (
    CourseCompletionStatusPerUser,
    CourseEnrollment,
    CourseStructure,
    Quiz,
    QuizAttemptHistory,
    QuizScore,
)

class DisplayClientCourseProgressView(ClientMixin,APIView):

    """
    GET request
    for user in request, if he has data in course enrollment table
    display if the user in request has active enrollment for the course
    display:
        completed_quiz_count
    """
    def get(self, request):
        try:
            # # Check if the user has client admin privileges
            if not self.has_client_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            user_id = request.query_params.get('user_id')

            # Validate request data
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has active enrollment for any course
            course_enrollments = CourseEnrollment.objects.filter(user_id=user_id, active=True)

            if not course_enrollments:
                return Response({'message': 'No active enrollment found for the user'}, status=status.HTTP_404_NOT_FOUND)

            # Display course progress for each active enrollment
            progress_data = []
            for enrollment in course_enrollments:
                quiz_score = QuizScore.objects.filter(course_id=enrollment.course_id, enrolled_user_id=user_id).first()
                if quiz_score:
                   
                    progress_percentage = 0
                    total_quiz_count = quiz_score.total_quizzes_per_course
                    completed_quiz_count = quiz_score.completed_quiz_count

                    # Determine completion_status or in_progress_status based on completed quiz count
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

            return Response({'progress': progress_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CountCoursesStatusView(ClientMixin,APIView):
    """
    GET request to count the number of active enrollments and course completion status for a user.
    """

    def get(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
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



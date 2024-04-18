from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path




from django.urls import path
from .views.clientdashboardviews import (
    CountCoursesStatusView,
    
    DisplayClientCourseProgressView,
    
    

)
from .views.scoreviews import (
   
    CourseCompletionStatusView,
    QuizScoreView,
   
    # EmployeeDashboard,
    CompleteQuizCountView,
    TotalScorePerCourseView,
    CourseCompletionStatusPerUserView,
    
    
    

)


from .views.superadmindashboardviews import (
    ActiveRegisteredCustomerCountView,
    CountOfActiveRegistrationPerCoure, 
    CourseCountView,
    GraphOfProgressPerCourseView, 
)

from .views.registercourseviews import (
    CourseCustomerRegistrationView,
    LMSCustomerListView,
    ManageCourseRegistrationRecordStatusView
)
from .views.coursesviews import (
    CourseView,
    ManageCourseView,
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
)
from .views.coursecontentviews import (
    CourseStructureView,
    ReadingMaterialView,
    QuizView,

)
from .views.quizcontentviews import (
    ChoicesView,
    QuestionView,
    QuizTake,
    # dummy_quiz_index,
)


urlpatterns = [
    #courseview.py  views url
    
    #coursemanagementviews.py views url

    
    #registercourseviews.py views url
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'),
    path('course-register-record/', CourseCustomerRegistrationView.as_view(), name='course-register-record'),
    path('manage-status/register-records/', ManageCourseRegistrationRecordStatusView.as_view(), name='manage-register-records'), 
        
    #superadmindashboardviews.py views url
    path('dashboard/sa/registration/count/', ActiveRegisteredCustomerCountView.as_view(), name='active-registration-count'),
    path('dashboard/sa/active_registration-per-course/count/', CountOfActiveRegistrationPerCoure.as_view(), name='active_registration-per-course-count'),
    path('dashboard/sa/progress-per-course/count/', GraphOfProgressPerCourseView.as_view(), name='not_started-per-course-count'),
    path('dashboard/sa/course/count/', CourseCountView.as_view(), name='course-count'),

    # coursesviews.py view urls
    path('courses/', CourseView.as_view(), name='courses'), #*
    path('manage/course/', ManageCourseView.as_view(), name='manage-course'), #*
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),
    
    # coursecontentviews.py view urls
    path('course/<int:course_id>/structure/', CourseStructureView.as_view(), name='course-structure'), #*
    path('course/<int:course_id>/reading-material/', ReadingMaterialView.as_view(), name='reading-material'), #*
    path('course/<int:course_id>/quiz/', QuizView.as_view(), name='quiz'), #*

    # quizcontentviews.py views urls
    path('quiz/<int:quiz_id>/question/', QuestionView.as_view(), name='reading-material'), #*
    path('question/<int:question_id>/choices/', ChoicesView.as_view(), name='question-choice'),
    path("<int:pk>/<slug:quiz_slug>/take/", QuizTake.as_view(), name="quiz_take"), #href="{% url 'quiz_take' pk=course.pk slug=quiz.slug %}
    #extra
    # path('quiz/redirect/<int:course_id>/', view=dummy_quiz_index, name='quiz_index'),
    path('course-completion-status/', CourseCompletionStatusView.as_view(), name='course_completion_status'),
    path('quiz-score/', QuizScoreView.as_view(), name='quiz_score'),
    path('complete-quiz-count/', CompleteQuizCountView.as_view(), name='complete_quiz_count'),
    path('total-score-per-course/', TotalScorePerCourseView.as_view(), name='total_score_per_course'),
    path('course-completion-status-per-user/', CourseCompletionStatusPerUserView.as_view(), name='course_completion_status_per_user'),
    path('display-client-course-progress/', DisplayClientCourseProgressView.as_view(), name='display_client_course_progress'),
    path('count-courses-status/', CountCoursesStatusView.as_view(), name='count_client_completed_courses'),
    # path('employee-dashboard/', EmployeeDashboard.as_view(), name='employee_dashboard'),

]



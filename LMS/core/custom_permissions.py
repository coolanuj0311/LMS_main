from rest_framework import permissions
from backend.models.allmodels import CourseEnrollment, CourseRegisterRecord
from core.custom_mixins import ClientAdminMixin, SuperAdminMixin,ClientMixin
from backend.models.coremodels import UserRolePrivileges

'''
allowed_resources:
1- LMS
2- Course Customer Registration
3- Course Enrollment
4- Courses
5- Course Management
6- Dashboard
'''

class SuperAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.has_super_admin_privileges(request)
    
class ClientAdminPermission(permissions.BasePermission, ClientAdminMixin):
    def has_permission(self, request, view):
        return self.has_client_admin_privileges(request)

class ClientPermission(permissions.BasePermission, ClientMixin):
    def has_permission(self, request, view):
        return self.has_client_privileges(request)


class SuperAdminOrAuthorizedOnly(permissions.BasePermission, SuperAdminMixin, ClientAdminMixin):
    
    def has_permission(self, request, view):
        if self.has_super_admin_privileges(request):
            return True

        if request.method == 'GET':
            user = request.data.get('user')
            course_id = request.kwargs.get('course_id')
            
            is_actively_enrolled = CourseEnrollment.objects.filter(course=course_id, user=user['id'], active=True).exists()
            if is_actively_enrolled:
                return True
            
            if self.has_client_admin_privileges(request):
                is_actively_registered = CourseRegisterRecord.objects.filter(course=course_id, customer=user['customer'], active=True).exists()
                if is_actively_registered:
                    return True

        return False
    
class SuperAdminOrGetOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if self.has_super_admin_privileges(request):
            return True
        if request.method == 'GET':
            return True
        else:
            return False

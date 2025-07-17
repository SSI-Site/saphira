
from django.urls.conf import path
from . import views

student_urls = [
    path('login', views.StudentLogin.as_view(), name='student-login'),
    path('<uuid:student_id>', views.StudentRetrieveUpdateView.as_view(), name='student-retrieve-update'),
    path('<uuid:student_id>/presence', views.CreateStudentOnlinePresenceView.as_view(), name='create-student-online-presence'),
    path('<uuid:student_id>/presences', views.RetrieveStudentPresencesView.as_view(), name='retrieve-student-presences'),
]

admin_students_urls = [
    path('admin/students', views.AdminListStudentsView.as_view(), name='admin-list-students'),
    path('admin/students/search/<name>', views.AdminListStudentsByNameView.as_view(), name='admin-list-students-by-name'),
    path('admin/students/<student_document>', views.AdminDestroyStudentView.as_view(), name='admin-destroy-student'),
]

admin_student_urls = [
    path('admin/student/<student_document>', views.AdminRetrieveStudentInfoView.as_view(), name='admin-retrieve-student-info'),
]

urlpatterns = student_urls

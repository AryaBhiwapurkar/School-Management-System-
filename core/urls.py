from django.urls import path
from .views import StudentRetrieveUpdateDeleteView, StudentListView, SectionStudentListCreateView, ClassSectionListCreateView, SectionRetrieveDeleteView, ClassListCreateView, ClassRetrieveDeleteView, SectionTeacherAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('students/',StudentListView.as_view()),
    path('students/<int:pk>/', StudentRetrieveUpdateDeleteView.as_view()),
    path('sections/<int:section_id>/students/', SectionStudentListCreateView.as_view()),
    path('classes/<int:class_id>/sections/', ClassSectionListCreateView.as_view()),
    path('sections/<int:pk>/', SectionRetrieveDeleteView.as_view()),
    path('classes/', ClassListCreateView.as_view()),
    path('classes/<int:pk>/', ClassRetrieveDeleteView.as_view()),
    path("sections/<int:section_id>/teacher/", SectionTeacherAPIView.as_view()),
]

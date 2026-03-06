from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError

from .models import Student, Section, Class, Teacher
from .serializers import (
    StudentSerializer,
    SectionSerializer,
    StudentReadSerializer,
    SectionReadSerializer,
    ClassMiniSerializer,
    ClassReadSerializer,
    ClassSerializer,
    TeacherMiniSerializer,
)
from .permissions import IsAdminOrReadOnly
from .filters import StudentFilter
from .logging_util import log_business_event


# ---------------- STUDENTS ---------------- #

class StudentListView(ListAPIView):
    serializer_class = StudentReadSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter

    def get_queryset(self):
        return Student.objects.select_related(
            "section",
            "section__school_class"
        ).order_by("section_id", "roll_number")


class StudentRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Student.objects.select_related(
            "section",
            "section__school_class"
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return StudentReadSerializer
        return StudentSerializer

    def perform_update(self, serializer):
        student = serializer.save()

        log_business_event(
            self.request,
            f"Student updated: id={student.id}, "
            f"roll_number={student.roll_number}, "
            f"section_id={student.section_id}"
        )

    def perform_destroy(self, instance):
        student_id = instance.id
        roll = instance.roll_number
        section_id = instance.section_id

        instance.delete()

        log_business_event(
            self.request,
            f"Student deleted: id={student_id}, "
            f"roll_number={roll}, "
            f"section_id={section_id}"
        )


class SectionStudentListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return StudentReadSerializer
        return StudentSerializer

    def get_section(self):
        return get_object_or_404(Section, pk=self.kwargs["section_id"])

    def get_queryset(self):
        return Student.objects.select_related(
            "section",
            "section__school_class"
        ).filter(section=self.get_section())

    def perform_create(self, serializer):
        section = self.get_section()
        student = serializer.save(section=section)

        log_business_event(
            self.request,
            f"Student created: id={student.id}, "
            f"roll_number={student.roll_number}, "
            f"section_id={section.id}"
        )


# ---------------- SECTIONS ---------------- #

class SectionRetrieveDeleteView(RetrieveDestroyAPIView):
    queryset = Section.objects.select_related("school_class")
    serializer_class = SectionReadSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_destroy(self, instance):
        section_id = instance.id
        class_id = instance.school_class_id
        section_label = instance.class_section

        instance.delete()

        log_business_event(
            self.request,
            f"Section deleted: id={section_id}, "
            f"class_id={class_id}, "
            f"class_section={section_label}"
        )


class ClassSectionListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SectionReadSerializer
        return SectionSerializer

    def get_school_class(self):
        return get_object_or_404(Class, pk=self.kwargs["class_id"])

    def get_queryset(self):
        return Section.objects.select_related("school_class").filter(
            school_class=self.get_school_class()
        )

    def perform_create(self, serializer):
        school_class = self.get_school_class()
        section = serializer.save(school_class=school_class)

        log_business_event(
            self.request,
            f"Section created: id={section.id}, "
            f"class_id={school_class.id}, "
            f"class_section={section.class_section}"
        )


# ---------------- CLASSES ---------------- #

class ClassListCreateView(ListCreateAPIView):
    queryset = Class.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ClassMiniSerializer
        return ClassSerializer

    def perform_create(self, serializer):
        school_class = serializer.save()

        log_business_event(
            self.request,
            f"Class created: id={school_class.id}, "
            f"grade={school_class.grade}, "
            f"academic_year={school_class.academic_year}"
        )


class ClassRetrieveDeleteView(RetrieveDestroyAPIView):
    queryset = Class.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        return ClassReadSerializer

    def perform_destroy(self, instance):
        class_id = instance.id
        grade = instance.grade
        year = instance.academic_year

        instance.delete()

        log_business_event(
            self.request,
            f"Class deleted: id={class_id}, "
            f"grade={grade}, "
            f"academic_year={year}"
        )


# ---------------- TEACHER ASSIGNMENT ---------------- #

class SectionTeacherAPIView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_section(self, section_id):
        return get_object_or_404(Section, pk=section_id)

    def get(self, request, section_id):
        section = self.get_section(section_id)
        teacher = section.class_teacher

        if teacher is None:
            return Response({"teacher": None}, status=status.HTTP_200_OK)

        serializer = TeacherMiniSerializer(teacher)
        return Response({"teacher": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, section_id):
        section = self.get_section(section_id)
        teacher_id = request.data.get("teacher_id")

        if teacher_id is None:
            raise ValidationError({
                "teacher_id": ["This field is required."]
            })

        teacher = get_object_or_404(Teacher, pk=teacher_id)

        existing_section = Section.objects.filter(
            class_teacher=teacher
        ).exclude(pk=section.pk).first()

        if existing_section:
            raise ValidationError({
                "teacher_id": [
                    "This teacher is already assigned to another section."
                ]
            })

        section.class_teacher = teacher
        section.save()

        log_business_event(
            request,
            f"Teacher assigned: "
            f"teacher_id={teacher.id}, "
            f"employee_id={teacher.employee_id}, "
            f"section_id={section.id}"
        )

        serializer = TeacherMiniSerializer(teacher)
        return Response({"teacher": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, section_id):
        section = self.get_section(section_id)

        if section.class_teacher is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        teacher_id = section.class_teacher.id
        employee_id = section.class_teacher.employee_id

        section.class_teacher = None
        section.save()

        log_business_event(
            request,
            f"Teacher removed: "
            f"teacher_id={teacher_id}, "
            f"employee_id={employee_id}, "
            f"section_id={section.id}"
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
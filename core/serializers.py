from rest_framework import serializers
from django.db import IntegrityError
from .models import Section, Student, Class, Teacher

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['section']


    def validate_roll_number(self, value):
        if not 1 <= value <= 100:
            raise serializers.ValidationError(
                "Roll number must be between 1 and 100"
            )
        return value


    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "roll_number": "Roll number already exists in this section"
            })


    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "roll_number": "Roll number already exists in this section"
            })
        

class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['school_class']


    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "class_section": "This section already exists in this class"
            })


    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "class_section": "This section already exists in this class"
            })



class ClassMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "grade", "academic_year"]


class SectionReadSerializer(serializers.ModelSerializer):
    school_class = ClassMiniSerializer(read_only=True)

    class Meta:
        model = Section
        fields = ["id", "class_section", "school_class"]


class StudentReadSerializer(serializers.ModelSerializer):
    section = SectionReadSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ["id", "name", "roll_number", "section"]


class ClassReadSerializer(serializers.ModelSerializer):
    sections = SectionReadSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ["id", "grade", "academic_year", "sections"]


class ClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = '__all__'

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "non_field_errors": [
                    "Class already exists for this academic year"
                ]
            })      
        

class TeacherMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ["id","name","employee_id"]
from django.db import models

# Create your models here.
class Class(models.Model):
    grade = models.IntegerField()
    academic_year = models.IntegerField()

    def __str__(self):
        return f'Grade {self.grade} ({self.academic_year})'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["grade","academic_year"],
                name="unique_class_per_academic_year"
            )
        ]

class Teacher(models.Model):
    name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"
    


class Section(models.Model):
    class_section = models.CharField(max_length=2)
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sections")
    class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sections"
    )


    def __str__(self):
        return f'{self.school_class} - {self.class_section}'
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school_class','class_section'],
                name = 'unique_section_per_class'
            )
        ]


class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.roll_number} - {self.name} - {self.section}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['section','roll_number'],
                name = 'unique_roll_per_section'
            )
        ]



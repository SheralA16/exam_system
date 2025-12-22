from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_file_size(file):
    """Valida que el archivo no exceda 5MB"""
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'El archivo no debe exceder {max_size_mb}MB. Tamaño actual: {file.size / (1024 * 1024):.2f}MB')
    return file


class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nombre del Curso')
    description = models.TextField(verbose_name='Descripción', blank=True, null=True)
    image = models.ImageField(
        upload_to='courses/',
        verbose_name='Imagen del Curso',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size
        ]
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['name']

    def __str__(self):
        return self.name


class Exam(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name='Curso',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200, verbose_name='Título del Tema')
    description = models.TextField(verbose_name='Descripción', blank=True, null=True)
    image = models.ImageField(
        upload_to='exams/',
        verbose_name='Imagen del Tema',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size
        ]
    )
    pdf_file = models.FileField(
        upload_to='exams/pdfs/',
        verbose_name='Archivo PDF',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['pdf']),
            validate_file_size
        ]
    )
    subject = models.CharField(max_length=100, verbose_name='Materia')
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Puntuación Total', default=0, null=True, blank=True)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Puntuación Mínima', default=0, null=True, blank=True)
    duration_minutes = models.IntegerField(verbose_name='Duración (minutos)', default=0, null=True, blank=True)
    exam_date = models.DateTimeField(verbose_name='Fecha del Tema', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_exams',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.course.name}"


class ExamResult(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('graded', 'Calificado'),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Examen'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_results',
        verbose_name='Estudiante',
        limit_choices_to={'user_type': 'student'}
    )
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntuación Obtenida',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    comments = models.TextField(verbose_name='Comentarios', blank=True, null=True)
    submitted_at = models.DateTimeField(verbose_name='Fecha de Envío', null=True, blank=True)
    graded_at = models.DateTimeField(verbose_name='Fecha de Calificación', null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='graded_results',
        verbose_name='Calificado por',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Resultado de Examen'
        verbose_name_plural = 'Resultados de Exámenes'
        unique_together = ('exam', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    def is_passed(self):
        if self.marks_obtained is not None:
            return self.marks_obtained >= self.exam.passing_marks
        return False

    def get_percentage(self):
        if self.marks_obtained is not None and self.exam.total_marks > 0:
            return (self.marks_obtained / self.exam.total_marks) * 100
        return 0


class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', 'Opción Múltiple'),
        ('true_false', 'Verdadero/Falso'),
        ('short_answer', 'Respuesta Corta'),
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Examen'
    )
    question_text = models.TextField(verbose_name='Pregunta')
    image = models.ImageField(
        upload_to='questions/',
        verbose_name='Imagen',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp']),
            validate_file_size
        ]
    )
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='multiple_choice',
        verbose_name='Tipo de Pregunta'
    )
    marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Puntuación', default=1.0)
    order = models.IntegerField(verbose_name='Orden', default=0)
    explanation = models.TextField(verbose_name='Comentario/Explicación', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['exam', 'order']

    def __str__(self):
        return f"{self.exam.title} - Pregunta {self.order}"


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Pregunta'
    )
    answer_text = models.TextField(verbose_name='Respuesta')
    is_correct = models.BooleanField(default=False, verbose_name='Es Correcta')
    order = models.IntegerField(verbose_name='Orden', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        ordering = ['question', 'order']

    def __str__(self):
        return f"{self.answer_text[:50]} - {'Correcta' if self.is_correct else 'Incorrecta'}"


class StudentAnswer(models.Model):
    exam_result = models.ForeignKey(
        ExamResult,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name='Resultado del Examen'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name='Pregunta'
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='selected_by',
        verbose_name='Respuesta Seleccionada',
        blank=True,
        null=True
    )
    text_answer = models.TextField(verbose_name='Respuesta de Texto', blank=True, null=True)
    is_correct = models.BooleanField(default=False, verbose_name='Es Correcta')
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntuación Obtenida',
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Respuesta del Estudiante'
        verbose_name_plural = 'Respuestas de Estudiantes'
        unique_together = ('exam_result', 'question')

    def __str__(self):
        return f"{self.exam_result.student.username} - {self.question}"


class CourseEnrollment(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Curso'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name='Estudiante',
        limit_choices_to={'user_type': 'student'}
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Inscripción')

    class Meta:
        verbose_name = 'Inscripción a Curso'
        verbose_name_plural = 'Inscripciones a Cursos'
        unique_together = ('course', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

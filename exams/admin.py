from django.contrib import admin
from .models import Course, Exam, ExamResult, Question, Answer, StudentAnswer, CourseEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'exam_date', 'total_marks', 'passing_marks', 'is_active', 'created_by')
    list_filter = ('is_active', 'subject', 'exam_date', 'created_at')
    search_fields = ('title', 'subject', 'description')
    date_hierarchy = 'exam_date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información del Examen', {
            'fields': ('title', 'description', 'subject')
        }),
        ('Puntuación', {
            'fields': ('total_marks', 'passing_marks')
        }),
        ('Fecha y Duración', {
            'fields': ('exam_date', 'duration_minutes')
        }),
        ('Estado', {
            'fields': ('is_active', 'created_by')
        }),
        ('Fechas de Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'status', 'submitted_at', 'graded_at')
    list_filter = ('status', 'exam', 'graded_at', 'submitted_at')
    search_fields = ('student__username', 'student__email', 'exam__title')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Información del Resultado', {
            'fields': ('exam', 'student', 'status')
        }),
        ('Calificación', {
            'fields': ('marks_obtained', 'comments')
        }),
        ('Información de Calificación', {
            'fields': ('graded_by', 'graded_at', 'submitted_at')
        }),
        ('Fechas de Registro', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ('answer_text', 'is_correct', 'order')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text_short', 'question_type', 'marks', 'order')
    list_filter = ('question_type', 'exam')
    search_fields = ('question_text', 'exam__title')
    inlines = [AnswerInline]

    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Pregunta'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer_text_short', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__exam')
    search_fields = ('answer_text', 'question__question_text')

    def answer_text_short(self, obj):
        return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
    answer_text_short.short_description = 'Respuesta'


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('exam_result', 'question', 'is_correct', 'marks_obtained')
    list_filter = ('is_correct', 'exam_result__exam')
    search_fields = ('exam_result__student__username', 'question__question_text')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__username', 'student__email', 'course__name')
    date_hierarchy = 'enrolled_at'

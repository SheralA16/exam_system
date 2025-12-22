from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Exam, Question, Answer
from django.http import JsonResponse
from django.db import models
from django_ratelimit.decorators import ratelimit


# ============ CURSO VIEWS ============
@login_required
def course_list(request):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'exams/course_list.html', context)


@login_required
def course_create(request):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        course = Course.objects.create(
            name=name,
            description=description,
            image=image,
            created_by=request.user
        )
        messages.success(request, f'Curso "{course.name}" creado exitosamente.')
        return redirect('exams:course_list')

    return render(request, 'exams/course_form.html')


@login_required
def course_edit(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.description = request.POST.get('description')
        if request.FILES.get('image'):
            course.image = request.FILES.get('image')
        course.save()
        messages.success(request, f'Curso "{course.name}" actualizado exitosamente.')
        return redirect('exams:course_list')

    context = {'course': course}
    return render(request, 'exams/course_form.html', context)


@login_required
def course_delete(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=pk)
    course_name = course.name
    course.delete()
    messages.success(request, f'Curso "{course_name}" eliminado exitosamente.')
    return redirect('exams:course_list')


# ============ EXAM VIEWS ============
@login_required
def exam_list(request, course_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=course_id)
    exams = course.exams.all()
    context = {'course': course, 'exams': exams}
    return render(request, 'exams/exam_list.html', context)


@login_required
def exam_create(request, course_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject = request.POST.get('subject')
        image = request.FILES.get('image')
        pdf_file = request.FILES.get('pdf_file')
        total_marks = request.POST.get('total_marks')
        passing_marks = request.POST.get('passing_marks')
        duration_minutes = request.POST.get('duration_minutes')
        exam_date = request.POST.get('exam_date')

        exam = Exam.objects.create(
            course=course,
            title=title,
            description=description,
            image=image,
            pdf_file=pdf_file,
            subject=subject,
            total_marks=total_marks,
            passing_marks=passing_marks,
            duration_minutes=duration_minutes,
            exam_date=exam_date,
            created_by=request.user
        )
        messages.success(request, f'Tema "{exam.title}" creado exitosamente.')
        return redirect('exams:question_manage', exam_id=exam.id)

    context = {'course': course}
    return render(request, 'exams/exam_form.html', context)


@login_required
def exam_edit(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    exam = get_object_or_404(Exam, pk=pk)

    if request.method == 'POST':
        exam.title = request.POST.get('title')
        exam.description = request.POST.get('description')
        exam.subject = request.POST.get('subject')
        if request.FILES.get('image'):
            exam.image = request.FILES.get('image')
        if request.FILES.get('pdf_file'):
            exam.pdf_file = request.FILES.get('pdf_file')
        exam.total_marks = request.POST.get('total_marks')
        exam.passing_marks = request.POST.get('passing_marks')
        exam.duration_minutes = request.POST.get('duration_minutes')
        exam.exam_date = request.POST.get('exam_date')
        exam.save()
        messages.success(request, f'Tema "{exam.title}" actualizado exitosamente.')
        return redirect('exams:exam_list', course_id=exam.course.id)

    context = {'exam': exam, 'course': exam.course}
    return render(request, 'exams/exam_form.html', context)


@login_required
def exam_delete(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    exam = get_object_or_404(Exam, pk=pk)
    course_id = exam.course.id
    exam_title = exam.title
    exam.delete()
    messages.success(request, f'Examen "{exam_title}" eliminado exitosamente.')
    return redirect('exams:exam_list', course_id=course_id)


# ============ QUESTION VIEWS ============
@login_required
@ratelimit(key='user', rate='100/h', method='POST', block=True)
def question_manage(request, exam_id):
    from django.core.paginator import Paginator

    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    exam = get_object_or_404(Exam, pk=exam_id)

    # Obtener parámetro de ordenamiento (por defecto: más reciente primero)
    order_by = request.GET.get('order', '-id')  # -id = descendente, id = ascendente

    # Obtener preguntas con ordenamiento
    questions = exam.questions.all().prefetch_related('answers').order_by(order_by)

    # Paginación - 40 preguntas por página
    paginator = Paginator(questions, 40)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        image = request.FILES.get('image')
        explanation = request.POST.get('explanation')
        answer_text = request.POST.get('answer_text')

        # Crear pregunta
        question = Question.objects.create(
            exam=exam,
            question_text=question_text,
            image=image,
            question_type='multiple_choice',
            marks=1.0,
            explanation=explanation,
            order=exam.questions.count() + 1
        )

        # Crear la respuesta única
        if answer_text:
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=True,
                order=1
            )

        messages.success(request, 'Pregunta creada exitosamente.')
        # Redirigir manteniendo el ordenamiento
        redirect_url = f"{request.path}?order={order_by}"
        return redirect(redirect_url)

    context = {
        'exam': exam,
        'questions': page_obj,
        'page_obj': page_obj,
        'order_by': order_by,
        'total_questions': questions.count(),
    }
    return render(request, 'exams/question_manage.html', context)


@login_required
def question_create(request, exam_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        image = request.FILES.get('image')
        explanation = request.POST.get('explanation')
        answer_text = request.POST.get('answer_text')

        # Crear pregunta
        question = Question.objects.create(
            exam=exam,
            question_text=question_text,
            image=image,
            question_type='multiple_choice',
            marks=1.0,
            explanation=explanation,
            order=exam.questions.count() + 1
        )

        # Crear la respuesta única
        if answer_text:
            Answer.objects.create(
                question=question,
                answer_text=answer_text,
                is_correct=True,
                order=1
            )

        messages.success(request, 'Pregunta creada exitosamente.')
        return redirect('exams:question_manage', exam_id=exam.id)

    context = {'exam': exam}
    return render(request, 'exams/question_form.html', context)


@login_required
def question_edit(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    question = get_object_or_404(Question, pk=pk)
    exam = question.exam

    if request.method == 'POST':
        question.question_text = request.POST.get('question_text')

        # Verificar si se quiere eliminar la imagen
        delete_image = request.POST.get('delete_image') == '1'
        if delete_image:
            question.image = None
        elif request.FILES.get('image'):
            question.image = request.FILES.get('image')

        question.explanation = request.POST.get('explanation')
        question.save()

        # Actualizar o crear la respuesta
        answer_text = request.POST.get('answer_text')
        if answer_text:
            answer = question.answers.first()
            if answer:
                answer.answer_text = answer_text
                answer.save()
            else:
                Answer.objects.create(
                    question=question,
                    answer_text=answer_text,
                    is_correct=True,
                    order=1
                )

        messages.success(request, 'Pregunta actualizada exitosamente.')
        return redirect('exams:question_manage', exam_id=exam.id)

    # Obtener la respuesta existente
    answer = question.answers.first()
    context = {
        'exam': exam,
        'question': question,
        'answer': answer
    }
    return render(request, 'exams/question_form.html', context)


@login_required
def question_delete(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    question = get_object_or_404(Question, pk=pk)
    exam_id = question.exam.id
    question.delete()
    messages.success(request, 'Pregunta eliminada exitosamente.')
    return redirect('exams:question_manage', exam_id=exam_id)


# ============ STUDENT VIEWS ============
@login_required
def student_course_exams(request, course_id):
    from .models import CourseEnrollment
    course = get_object_or_404(Course, pk=course_id)

    # Verificar que el estudiante esté inscrito en el curso
    if request.user.is_student():
        enrollment = CourseEnrollment.objects.filter(course=course, student=request.user).first()
        if not enrollment:
            messages.error(request, 'No estás inscrito en este curso.')
            return redirect('accounts:dashboard')

    exams = course.exams.filter(is_active=True)
    context = {'course': course, 'exams': exams}
    return render(request, 'exams/student_exams.html', context)


@login_required
def student_take_exam(request, exam_id):
    from django.core.paginator import Paginator
    from django.db.models import Q

    exam = get_object_or_404(Exam, pk=exam_id, is_active=True)

    # Verificar inscripción
    if request.user.is_student():
        from .models import CourseEnrollment
        enrollment = CourseEnrollment.objects.filter(course=exam.course, student=request.user).first()
        if not enrollment:
            messages.error(request, 'No estás inscrito en este curso.')
            return redirect('accounts:dashboard')

    # Obtener todas las preguntas y respuestas
    questions = exam.questions.all().prefetch_related('answers').order_by('order')

    # Búsqueda
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # Buscar solo por texto de pregunta
        questions = questions.filter(question_text__icontains=search_query)

    # Paginación - 40 preguntas por página
    paginator = Paginator(questions, 40)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'exam': exam,
        'questions': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'total_questions': questions.count(),
    }
    return render(request, 'exams/student_view_exam.html', context)


@login_required
def student_exam_result(request, exam_result_id):
    exam_result = get_object_or_404(ExamResult, pk=exam_result_id, student=request.user)
    student_answers = exam_result.student_answers.all().select_related('question', 'selected_answer')

    context = {
        'exam_result': exam_result,
        'student_answers': student_answers,
    }
    return render(request, 'exams/student_result.html', context)


@login_required
def student_view_pdf(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id, is_active=True)

    # Verificar inscripción
    if request.user.is_student():
        from .models import CourseEnrollment
        enrollment = CourseEnrollment.objects.filter(course=exam.course, student=request.user).first()
        if not enrollment:
            messages.error(request, 'No estás inscrito en este curso.')
            return redirect('accounts:dashboard')

    # Verificar que el examen tenga PDF
    if not exam.pdf_file:
        messages.error(request, 'Este tema no tiene un archivo PDF disponible.')
        return redirect('exams:student_take_exam', exam_id=exam.id)

    context = {
        'exam': exam,
    }
    return render(request, 'exams/student_view_pdf.html', context)

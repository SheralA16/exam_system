from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('accounts:login')


@login_required
def dashboard_view(request):
    user = request.user
    context = {
        'user': user,
    }

    if user.is_admin():
        return render(request, 'accounts/dashboard_admin.html', context)
    else:
        from exams.models import CourseEnrollment
        enrollments = CourseEnrollment.objects.filter(student=user).select_related('course')
        context['enrollments'] = enrollments
        return render(request, 'accounts/dashboard_student.html', context)


@login_required
def student_list(request):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    students = User.objects.filter(user_type='student').order_by('username')
    context = {'students': students}
    return render(request, 'accounts/student_list.html', context)


@login_required
def student_assign_courses(request, student_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    from exams.models import Course, CourseEnrollment

    student = get_object_or_404(User, pk=student_id, user_type='student')
    all_courses = Course.objects.filter(is_active=True)
    enrolled_courses = CourseEnrollment.objects.filter(student=student).values_list('course_id', flat=True)

    if request.method == 'POST':
        selected_courses = request.POST.getlist('courses')

        # Eliminar inscripciones existentes
        CourseEnrollment.objects.filter(student=student).delete()

        # Crear nuevas inscripciones
        for course_id in selected_courses:
            course = Course.objects.get(pk=course_id)
            CourseEnrollment.objects.create(student=student, course=course)

        messages.success(request, f'Cursos asignados a {student.username} exitosamente.')
        return redirect('accounts:student_list')

    context = {
        'student': student,
        'all_courses': all_courses,
        'enrolled_courses': list(enrolled_courses),
    }
    return render(request, 'accounts/student_assign_courses.html', context)


@login_required
def user_list(request):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    from django.utils import timezone
    from datetime import timedelta

    users = User.objects.all().order_by('-date_joined')

    # Calcular si cada usuario está en línea (último acceso hace menos de 15 minutos)
    now = timezone.now()
    for user in users:
        if user.last_login:
            time_diff = now - user.last_login
            user.is_online = time_diff < timedelta(minutes=15)
        else:
            user.is_online = False

    context = {'users': users}
    return render(request, 'accounts/user_list.html', context)


@login_required
def create_user(request):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')

        # Validaciones
        if not username or not password:
            messages.error(request, 'El nombre de usuario y la contraseña son obligatorios.')
            return render(request, 'accounts/create_user.html')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/create_user.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'El nombre de usuario "{username}" ya existe.')
            return render(request, 'accounts/create_user.html')

        if email and User.objects.filter(email=email).exists():
            messages.error(request, f'El correo electrónico "{email}" ya está registrado.')
            return render(request, 'accounts/create_user.html')

        # Crear el usuario
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                user_type=user_type
            )
            user_type_display = 'Administrador' if user_type == 'admin' else 'Estudiante'
            messages.success(request, f'{user_type_display} "{username}" creado exitosamente.')
            return redirect('accounts:user_list')
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
            return render(request, 'accounts/create_user.html')

    return render(request, 'accounts/create_user.html')


@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        user_to_toggle = get_object_or_404(User, pk=user_id)

        # Evitar que el admin se desactive a sí mismo
        if user_to_toggle.id == request.user.id:
            messages.error(request, 'No puedes cambiar tu propio estado.')
            return redirect('accounts:user_list')

        # Cambiar el estado
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save()

        status_text = 'activado' if user_to_toggle.is_active else 'desactivado'
        messages.success(request, f'Usuario "{user_to_toggle.username}" {status_text} exitosamente.')

    return redirect('accounts:user_list')


@login_required
def edit_user(request, user_id):
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    user_to_edit = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        # Validar username único (excepto el actual)
        if User.objects.filter(username=username).exclude(pk=user_id).exists():
            messages.error(request, f'El nombre de usuario "{username}" ya existe.')
            return render(request, 'accounts/edit_user.html', {'user_to_edit': user_to_edit})

        # Validar email único (excepto el actual)
        if email and User.objects.filter(email=email).exclude(pk=user_id).exists():
            messages.error(request, f'El correo electrónico "{email}" ya está registrado.')
            return render(request, 'accounts/edit_user.html', {'user_to_edit': user_to_edit})

        # Validar contraseñas si se están cambiando
        if password:
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'accounts/edit_user.html', {'user_to_edit': user_to_edit})

        # Actualizar datos
        try:
            user_to_edit.username = username
            user_to_edit.first_name = first_name
            user_to_edit.last_name = last_name
            user_to_edit.email = email
            user_to_edit.user_type = user_type

            # Cambiar contraseña solo si se proporcionó una nueva
            if password:
                user_to_edit.set_password(password)

            user_to_edit.save()

            messages.success(request, f'Usuario "{username}" actualizado exitosamente.')
            return redirect('accounts:user_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
            return render(request, 'accounts/edit_user.html', {'user_to_edit': user_to_edit})

    context = {'user_to_edit': user_to_edit}
    return render(request, 'accounts/edit_user.html', context)

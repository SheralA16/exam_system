from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django_ratelimit.decorators import ratelimit
from .models import LoginReactivationRequest
from django.utils import timezone

User = get_user_model()

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verificar si el usuario está deshabilitado por límite de inicios
            if user.is_disabled_by_login_limit:
                messages.error(
                    request,
                    'Tu cuenta ha sido deshabilitada por exceder el límite de inicios de sesión permitidos. '
                    'Por favor, solicita la reactivación de tu cuenta.'
                )
                return render(request, 'accounts/login.html', {'show_reactivation_button': True, 'disabled_user': user})

            # Incrementar contador de inicios de sesión (solo para estudiantes)
            if user.is_student():
                is_still_active = user.increment_login_count()

                if not is_still_active:
                    messages.error(
                        request,
                        f'Has alcanzado el límite máximo de {user.max_logins_allowed} inicios de sesión. '
                        'Tu cuenta ha sido deshabilitada. Por favor, solicita la reactivación.'
                    )
                    return render(request, 'accounts/login.html', {'show_reactivation_button': True, 'disabled_user': user})

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
        # Contar solicitudes pendientes de reactivación
        pending_reactivation_count = LoginReactivationRequest.objects.filter(status='pending').count()
        context['pending_reactivation_count'] = pending_reactivation_count
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
@ratelimit(key='user', rate='20/h', method='POST', block=True)
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


@ratelimit(key='ip', rate='5/h', method='POST', block=True)
def request_reactivation(request):
    """Vista para que los estudiantes soliciten la reactivación de su cuenta"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        message = request.POST.get('message', '')

        try:
            user = User.objects.get(pk=user_id, is_disabled_by_login_limit=True)

            # Verificar si ya tiene una solicitud pendiente
            pending_request = LoginReactivationRequest.objects.filter(
                user=user,
                status='pending'
            ).first()

            if pending_request:
                messages.warning(request, 'Ya tienes una solicitud de reactivación pendiente.')
            else:
                # Crear nueva solicitud
                LoginReactivationRequest.objects.create(
                    user=user,
                    message=message
                )
                messages.success(
                    request,
                    'Tu solicitud de reactivación ha sido enviada al administrador. '
                    'Recibirás una respuesta pronto.'
                )

        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')

    return redirect('accounts:login')


@login_required
def reactivation_requests(request):
    """Vista para que el admin vea y gestione solicitudes de reactivación"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('accounts:dashboard')

    # Obtener todas las solicitudes ordenadas por estado y fecha
    pending_requests = LoginReactivationRequest.objects.filter(status='pending').order_by('-requested_at')
    processed_requests = LoginReactivationRequest.objects.exclude(status='pending').order_by('-processed_at')

    context = {
        'pending_requests': pending_requests,
        'processed_requests': processed_requests,
    }
    return render(request, 'accounts/reactivation_requests.html', context)


@login_required
def approve_reactivation(request, request_id):
    """Vista para que el admin apruebe una solicitud de reactivación"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        reactivation_request = get_object_or_404(LoginReactivationRequest, pk=request_id)
        admin_response = request.POST.get('admin_response', '')

        reactivation_request.approve(request.user, admin_response)

        messages.success(
            request,
            f'Solicitud aprobada. El usuario "{reactivation_request.user.username}" ha sido reactivado.'
        )

    return redirect('accounts:reactivation_requests')


@login_required
def reject_reactivation(request, request_id):
    """Vista para que el admin rechace una solicitud de reactivación"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        reactivation_request = get_object_or_404(LoginReactivationRequest, pk=request_id)
        admin_response = request.POST.get('admin_response', '')

        reactivation_request.reject(request.user, admin_response)

        messages.success(request, f'Solicitud rechazada.')

    return redirect('accounts:reactivation_requests')


@login_required
def reset_user_login_count(request, user_id):
    """Vista para que el admin resetee manualmente el contador de inicios de sesión"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        user_to_reset = get_object_or_404(User, pk=user_id)

        if user_to_reset.is_student():
            user_to_reset.reset_login_count()
            messages.success(
                request,
                f'Contador de inicios de sesión reseteado para "{user_to_reset.username}". '
                f'El usuario ha sido reactivado.'
            )
        else:
            messages.error(request, 'Solo se puede resetear el contador de estudiantes.')

    return redirect('accounts:user_list')

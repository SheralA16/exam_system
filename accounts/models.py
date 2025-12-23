from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('student', 'Estudiante'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name='Tipo de Usuario'
    )

    # Campos para control de inicios de sesión (solo para estudiantes)
    login_count = models.IntegerField(
        default=0,
        verbose_name='Contador de Inicios de Sesión'
    )
    max_logins_allowed = models.IntegerField(
        default=2,
        verbose_name='Máximo de Inicios de Sesión Permitidos'
    )
    is_disabled_by_login_limit = models.BooleanField(
        default=False,
        verbose_name='Deshabilitado por Límite de Inicios'
    )
    last_login_attempt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último Intento de Inicio de Sesión'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_admin(self):
        return self.user_type == 'admin'

    def is_student(self):
        return self.user_type == 'student'

    def increment_login_count(self):
        """Incrementa el contador de inicios de sesión y verifica el límite"""
        if self.is_student():
            self.login_count += 1
            self.last_login_attempt = timezone.now()

            # Deshabilitar solo cuando EXCEDE el límite (3er intento con max=2)
            if self.login_count > self.max_logins_allowed:
                self.is_active = False
                self.is_disabled_by_login_limit = True

            self.save()
            return self.is_active
        return True

    def reset_login_count(self):
        """Resetea el contador de inicios de sesión y habilita la cuenta"""
        self.login_count = 0
        self.is_active = True
        self.is_disabled_by_login_limit = False
        self.last_login_attempt = None
        self.save()


class LoginReactivationRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reactivation_requests',
        verbose_name='Usuario'
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Solicitud'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    message = models.TextField(
        blank=True,
        verbose_name='Mensaje del Estudiante'
    )
    admin_response = models.TextField(
        blank=True,
        verbose_name='Respuesta del Administrador'
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_requests',
        verbose_name='Procesado por'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Procesamiento'
    )

    class Meta:
        verbose_name = 'Solicitud de Reactivación'
        verbose_name_plural = 'Solicitudes de Reactivación'
        ordering = ['-requested_at']

    def __str__(self):
        return f"Solicitud de {self.user.username} - {self.get_status_display()}"

    def approve(self, admin_user, response=''):
        """Aprueba la solicitud y habilita al usuario"""
        self.status = 'approved'
        self.admin_response = response
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.save()

        # Resetear el contador del usuario
        self.user.reset_login_count()

    def reject(self, admin_user, response=''):
        """Rechaza la solicitud"""
        self.status = 'rejected'
        self.admin_response = response
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        self.save()

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un superusuario si no existe'

    def handle(self, *args, **options):
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@uss.edu.pe')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='admin123')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING(f'El superusuario "{username}" ya existe'))

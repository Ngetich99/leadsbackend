from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a default superuser if none exists'
    
    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email='admin@crm.com',
                username='admin',
                password='admin123',
                role='manager'
            )
            self.stdout.write(self.style.SUCCESS('Default superuser created'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))

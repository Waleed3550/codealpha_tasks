import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.users.models import User

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    su = superusers.first()
    su.set_password('admin123')
    su.save()
    print(f"Password for existing superuser ({su.email}) reset to: admin123")
else:
    su = User.objects.create_superuser('admin@admin.com', 'admin123')
    print(f"Created new superuser: admin@admin.com with password: admin123")

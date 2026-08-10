import os
import django
import sys
from django.apps import apps
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

def generate_admin_files():
    project_apps = [app.label for app in apps.get_app_configs() if app.name.startswith('apps.') or app.name == 'core']
    
    for app_label in project_apps:
        app_config = apps.get_app_config(app_label)
        models = app_config.get_models()
        
        model_names = [model.__name__ for model in models]
        if not model_names:
            continue
            
        admin_content = f"from django.contrib import admin\nfrom .models import {', '.join(model_names)}\n\n"
        for name in model_names:
            admin_content += f"@admin.register({name})\nclass {name}Admin(admin.ModelAdmin):\n    pass\n\n"
            
        admin_path = os.path.join(app_config.path, 'admin.py')
        
        with open(admin_path, 'w') as f:
            f.write(admin_content)
        print(f"Generated admin.py for {app_label}")

if __name__ == '__main__':
    generate_admin_files()

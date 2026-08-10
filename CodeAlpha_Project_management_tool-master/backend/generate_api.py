import os
import re

APPS_DIR = r"D:\management_tool\backend\apps"
APPS = ['audit', 'calendar', 'chat', 'comments', 'files', 'notifications', 'organizations', 'projects']

for app_name in APPS:
    app_path = os.path.join(APPS_DIR, app_name)
    models_file = os.path.join(app_path, 'models.py')
    
    if not os.path.exists(models_file):
        continue
        
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    models = re.findall(r'class\s+([A-Za-z0-9_]+)\(.*?Model.*?\):', content)
    models = [m for m in models if m not in ('BaseModel', 'AbstractUser')]
    
    if not models:
        continue
        
    print(f"Processing {app_name}: {models}")
    
    # Generate serializers.py
    serializers_path = os.path.join(app_path, 'serializers.py')
    if not os.path.exists(serializers_path):
        code = "from rest_framework import serializers\n"
        code += f"from .models import {', '.join(models)}\n\n"
        for m in models:
            code += f"class {m}Serializer(serializers.ModelSerializer):\n"
            code += f"    class Meta:\n"
            code += f"        model = {m}\n"
            code += f"        fields = '__all__'\n\n"
        with open(serializers_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
    # Generate views.py
    views_path = os.path.join(app_path, 'views.py')
    if not os.path.exists(views_path):
        code = "from rest_framework import viewsets\n"
        code += "from rest_framework.permissions import IsAuthenticated\n"
        code += f"from .models import {', '.join(models)}\n"
        code += f"from .serializers import {', '.join([m + 'Serializer' for m in models])}\n\n"
        for m in models:
            code += f"class {m}ViewSet(viewsets.ModelViewSet):\n"
            code += f"    queryset = {m}.objects.all()\n"
            code += f"    serializer_class = {m}Serializer\n"
            code += f"    permission_classes = [IsAuthenticated]\n\n"
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
    # Generate urls.py
    urls_path = os.path.join(app_path, 'urls.py')
    if not os.path.exists(urls_path):
        code = "from django.urls import path, include\n"
        code += "from rest_framework.routers import DefaultRouter\n"
        code += f"from .views import {', '.join([m + 'ViewSet' for m in models])}\n\n"
        code += "router = DefaultRouter()\n"
        for m in models:
            url_name = m.lower() + 's'
            if url_name.endswith('ss'): url_name = url_name[:-1]
            code += f"router.register(r'{url_name}', {m}ViewSet, basename='{m.lower()}')\n"
        code += "\nurlpatterns = [\n    path('', include(router.urls)),\n]\n"
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
print("Done!")

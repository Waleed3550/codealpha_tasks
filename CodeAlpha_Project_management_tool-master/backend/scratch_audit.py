import os
import ast

def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return {'classes': classes, 'functions': funcs}
    except Exception as e:
        return str(e)

apps_dir = 'apps'
for app in os.listdir(apps_dir):
    app_path = os.path.join(apps_dir, app)
    if os.path.isdir(app_path):
        print(f'\n--- APP: {app} ---')
        for file in ['models.py', 'serializers.py', 'views.py', 'urls.py', 'services.py', 'consumers.py']:
            filepath = os.path.join(app_path, file)
            if os.path.exists(filepath):
                info = analyze_file(filepath)
                if isinstance(info, dict):
                    print(f'  {file}: Classes={info["classes"]}, Functions={info["functions"]}')
                else:
                    print(f'  {file}: Error parsing')

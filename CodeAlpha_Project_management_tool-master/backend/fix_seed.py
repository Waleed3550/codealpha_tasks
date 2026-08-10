import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.users.models import User
from apps.organizations.models import Workspace, WorkspaceMember
from apps.tasks.models import Task, TaskAssignment
from apps.projects.models import Project

user = User.objects.first()
if user:
    # Fix Workspace
    for ws in Workspace.objects.all():
        WorkspaceMember.objects.get_or_create(workspace=ws, user=user)
        print(f'Added user to workspace {ws.name}')

    # Fix Tasks
    for task in Task.objects.all():
        TaskAssignment.objects.get_or_create(task=task, user=user)
        print(f'Assigned task {task.title} to user')

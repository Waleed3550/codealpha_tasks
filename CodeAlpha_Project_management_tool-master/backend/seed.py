import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.users.models import User
from apps.organizations.models import Organization, Workspace
from apps.projects.models import Project, Board, Column
from apps.tasks.models import Task, Tag
from django.utils import timezone

def run():
    print("Seeding database...")
    
    # 1. User
    user, created = User.objects.get_or_create(
        email='admin@nexus.com',
        defaults={'first_name': 'Admin', 'last_name': 'User'}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("Created Admin User")

    # 2. Organization & Workspace
    org, _ = Organization.objects.get_or_create(name='Nexus Corp', owner=user)
    workspace, _ = Workspace.objects.get_or_create(organization=org, name='Engineering Workspace')
    
    # 3. Project & Board
    project, _ = Project.objects.get_or_create(
        workspace=workspace, 
        name='Nexus Core V2',
        defaults={'owner': user, 'description': 'Enterprise Project Management Redesign'}
    )
    board, _ = Board.objects.get_or_create(project=project, name='Main Kanban Board')
    
    # 4. Columns
    col_todo, _ = Column.objects.get_or_create(board=board, title='To Do', defaults={'color': 'bg-slate-500', 'order': 1})
    col_in_progress, _ = Column.objects.get_or_create(board=board, title='In Progress', defaults={'color': 'bg-blue-500', 'order': 2})
    col_review, _ = Column.objects.get_or_create(board=board, title='Review', defaults={'color': 'bg-purple-500', 'order': 3})
    col_done, _ = Column.objects.get_or_create(board=board, title='Completed', defaults={'color': 'bg-emerald-500', 'order': 4})
    
    # 5. Tags
    tag_design, _ = Tag.objects.get_or_create(name='Design')
    tag_devops, _ = Tag.objects.get_or_create(name='DevOps')
    tag_frontend, _ = Tag.objects.get_or_create(name='Frontend')
    tag_backend, _ = Tag.objects.get_or_create(name='Backend')
    
    # 6. Tasks
    if not Task.objects.exists():
        t1 = Task.objects.create(project=project, column=col_todo, title='Design Landing Page', priority='High', status=str(col_todo.id))
        t1.tags.add(tag_design)
        
        t2 = Task.objects.create(project=project, column=col_todo, title='Setup CI/CD Pipeline', priority='High', status=str(col_todo.id))
        t2.tags.add(tag_devops)
        
        t3 = Task.objects.create(project=project, column=col_in_progress, title='Kanban Component Logic', priority='Medium', status=str(col_in_progress.id))
        t3.tags.add(tag_frontend)
        
        t4 = Task.objects.create(project=project, column=col_review, title='Authentication API', priority='High', status=str(col_review.id))
        t4.tags.add(tag_backend)
        
        print("Created Tasks")
    
    print("Database seeding complete. Live data is ready for the frontend.")

if __name__ == '__main__':
    run()

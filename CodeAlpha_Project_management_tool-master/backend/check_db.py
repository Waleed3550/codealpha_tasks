import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.chat.models import ChatRoom
from apps.organizations.models import Workspace, WorkspaceMember
from apps.users.models import User

user = User.objects.get(email='testuser_fiwpb@example.com')
print(f"User is_superuser: {user.is_superuser}")

member = WorkspaceMember.objects.filter(user=user).first()
if member:
    print(f"Found workspace: {member.workspace.name}")
else:
    print("No workspace found for user!")

rooms = ChatRoom.objects.all()
print(f"Total ChatRooms in DB: {rooms.count()}")
for r in rooms:
    print(f" - {r.name} in {r.workspace.name}")

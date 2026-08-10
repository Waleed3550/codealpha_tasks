import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.organizations.models import Workspace
from apps.chat.models import ChatRoom

workspace = Workspace.objects.first()
if workspace:
    ChatRoom.objects.get_or_create(workspace=workspace, name='general', room_type='organization')
    ChatRoom.objects.get_or_create(workspace=workspace, name='engineering', room_type='group')
    print('Chat rooms seeded.')

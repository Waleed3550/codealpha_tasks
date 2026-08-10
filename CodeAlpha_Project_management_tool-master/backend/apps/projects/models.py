from django.db import models
from core.models import BaseModel
from apps.organizations.models import Workspace, Role
from apps.users.models import User

class Project(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Using CharField with choices is standard, we define simple string default for now
    status = models.CharField(max_length=50, default='planning', db_index=True) 

    # Phase 3 Fields
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_projects')
    color = models.CharField(max_length=20, default="#4F46E5") # Default Indigo
    icon = models.CharField(max_length=50, blank=True, default="briefcase")
    is_template = models.BooleanField(default=False)
    
    PERMISSION_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('team', 'Team Only'),
    ]
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='team')
    
    def __str__(self):
        return self.name

class ProjectMember(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('project', 'user')
        
    def __str__(self):
        return f"{self.user.email} in {self.project.name}"

class ProjectActivity(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.action} on {self.project.name}"

class Board(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(max_length=255, default='Main Board')
    description = models.TextField(blank=True)
    settings = models.JSONField(default=dict)

    def __str__(self):
        return self.name

class Column(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=20, default='bg-slate-500')
    order = models.IntegerField(default=0)
    wip_limit = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} - {self.board.name}"

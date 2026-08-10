from django.db import models
from core.models import BaseModel
from apps.users.models import User

class Organization(BaseModel):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_organizations')
    domain = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    logo = models.ImageField(upload_to='organizations/logos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Workspace(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='workspaces')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class Team(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    
    def __str__(self):
        return self.name

class Role(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    # Storing custom granular permissions as JSON (e.g. {"tasks:create": true, "tasks:delete": false})
    permissions = models.JSONField(default=dict) 
    
    def __str__(self):
        return f"{self.name} in {self.workspace.name}"

class WorkspaceMember(BaseModel):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name='members', null=True, blank=True)

    class Meta:
        unique_together = ('workspace', 'user')
        
    def __str__(self):
        role_name = self.role.name if self.role else 'No Role'
        return f"{self.user.email} - {role_name} in {self.workspace.name}"

class SystemSettings(BaseModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=50, default='system')
    language = models.CharField(max_length=20, default='en-US')
    timezone = models.CharField(max_length=100, default='UTC')
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    security_2fa_required = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Settings for {self.organization.name}"

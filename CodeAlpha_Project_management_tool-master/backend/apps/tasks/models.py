from django.db import models
from core.models import BaseModel
from apps.projects.models import Project, Column
from apps.users.models import User

class Tag(BaseModel):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="#000000")
    
    def __str__(self):
        return self.name

class Task(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    column = models.ForeignKey(Column, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=100, default='todo', db_index=True)
    priority = models.CharField(max_length=50, default='medium', db_index=True)
    
    start_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True, db_index=True)
    estimated_time = models.FloatField(null=True, blank=True, help_text="Estimated hours")
    actual_time = models.FloatField(null=True, blank=True, help_text="Actual hours logged")
    
    # Support for infinite nesting of subtasks
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    tags = models.ManyToManyField(Tag, related_name='tasks', blank=True)

    def __str__(self):
        return self.title

class TaskAssignment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    
    class Meta:
        unique_together = ('task', 'user')

class Checklist(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.title} for {self.task.title}"

class ChecklistItem(BaseModel):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items')
    content = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content

class TaskDependency(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='depends_on')
    depends_on_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='blocking')
    type = models.CharField(max_length=50, default='blocking') # e.g. blocking, related_to
    
    class Meta:
        unique_together = ('task', 'depends_on_task')
        
    def __str__(self):
        return f"{self.task.title} depends on {self.depends_on_task.title}"

from django.contrib import admin
from .models import Tag, Task, TaskAssignment, Checklist, ChecklistItem, TaskDependency

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    pass

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    pass

@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    pass


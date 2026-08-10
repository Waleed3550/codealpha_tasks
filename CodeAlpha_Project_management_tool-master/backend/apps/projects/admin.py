from django.contrib import admin
from .models import Project, ProjectMember, ProjectActivity, Board, Column

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    pass

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    pass


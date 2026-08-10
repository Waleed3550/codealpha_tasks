from django.contrib import admin
from .models import Comment, Reply, Reaction

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    pass

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    pass


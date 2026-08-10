from rest_framework import serializers
from .models import Task, Checklist, ChecklistItem, Tag
from apps.comments.models import Comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'text', 'is_completed', 'order']

class ChecklistSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Checklist
        fields = ['id', 'name', 'items']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['author', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    checklists = ChecklistSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    assignees_data = serializers.SerializerMethodField()
    assignees = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'title', 'description', 'status', 'priority', 
            'start_date', 'due_date', 'tags', 'checklists', 'comments', 
            'assignees', 'assignees_data', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        assignees = validated_data.pop('assignees', [])
        task = super().create(validated_data)
        from .models import TaskAssignment
        for user_id in assignees:
            TaskAssignment.objects.create(task=task, user_id=user_id)
        return task

    def update(self, instance, validated_data):
        assignees = validated_data.pop('assignees', None)
        task = super().update(instance, validated_data)
        if assignees is not None:
            from .models import TaskAssignment
            TaskAssignment.objects.filter(task=task).delete()
            for user_id in assignees:
                TaskAssignment.objects.create(task=task, user_id=user_id)
        return task

    def get_assignees_data(self, obj):
        return [{"id": a.user.id, "username": a.user.username} for a in obj.assignments.all()]

    def get_comments(self, obj):
        from apps.comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        comments = Comment.objects.filter(content_type=ct, object_id=obj.id)
        return CommentSerializer(comments, many=True).data

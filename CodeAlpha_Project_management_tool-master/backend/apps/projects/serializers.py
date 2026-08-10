from rest_framework import serializers
from .models import Project, ProjectMember, ProjectActivity

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        project = super().create(validated_data)
        from .models import Board, Column
        board = Board.objects.create(project=project, name="Main Kanban Board")
        Column.objects.create(board=board, title="To Do", color="bg-slate-500", order=1)
        Column.objects.create(board=board, title="In Progress", color="bg-blue-500", order=2)
        Column.objects.create(board=board, title="Review", color="bg-purple-500", order=3)
        Column.objects.create(board=board, title="Completed", color="bg-emerald-500", order=4)
        return project

class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = '__all__'

class ProjectActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectActivity
        fields = '__all__'

from .models import Board, Column

class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = '__all__'

class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = '__all__'

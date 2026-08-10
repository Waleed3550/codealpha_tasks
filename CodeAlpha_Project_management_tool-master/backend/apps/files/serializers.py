from rest_framework import serializers
from .models import Attachment
from django.contrib.contenttypes.models import ContentType

class AttachmentSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(write_only=True, required=False)
    uploader_name = serializers.CharField(source='uploader.get_full_name', read_only=True)

    class Meta:
        model = Attachment
        fields = [
            'id', 'file', 'file_name', 'file_size', 'mime_type', 
            'version', 'model_name', 'object_id', 'uploader_name', 'created_at'
        ]
        read_only_fields = ['file_size', 'mime_type', 'uploader']

    def create(self, validated_data):
        model_name = validated_data.pop('model_name', None)
        if model_name:
            validated_data['content_type'] = ContentType.objects.get(model=model_name.lower())
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploader'] = request.user
            
        file_obj = validated_data.get('file')
        if file_obj:
            if not validated_data.get('file_name'):
                validated_data['file_name'] = file_obj.name
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = file_obj.content_type

        return super().create(validated_data)

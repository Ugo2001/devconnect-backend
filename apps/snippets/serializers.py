# ============================================================================
# apps/snippets/serializers.py
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Snippet, Language, SnippetComment, SnippetLike

User = get_user_model()


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'slug', 'extension', 'color', 'snippets_count']
        read_only_fields = ['id', 'slug', 'snippets_count']


class SnippetCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    
    class Meta:
        model = SnippetComment
        fields = [
            'id', 'snippet', 'author', 'content', 'line_number',
            'likes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'likes_count', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }


class SnippetListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    language = LanguageSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    code_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Snippet
        fields = [
            'id', 'title', 'slug', 'description', 'code_preview',
            'author', 'language', 'visibility', 'tags',
            'views_count', 'likes_count', 'forks_count',
            'created_at', 'updated_at', 'is_liked'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'avatar': obj.author.avatar.url if obj.author.avatar else None
        }
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SnippetLike.objects.filter(user=request.user, snippet=obj).exists()
        return False
    
    def get_code_preview(self, obj):
        # Return first 5 lines for preview
        lines = obj.code.split('\n')[:5]
        return '\n'.join(lines)


class SnippetDetailSerializer(SnippetListSerializer):
    comments = SnippetCommentSerializer(many=True, read_only=True)
    forked_from_snippet = serializers.SerializerMethodField()
    
    class Meta(SnippetListSerializer.Meta):
        fields = SnippetListSerializer.Meta.fields + ['code', 'comments', 'forked_from_snippet']
    
    def get_forked_from_snippet(self, obj):
        if obj.forked_from:
            return {
                'id': obj.forked_from.id,
                'title': obj.forked_from.title,
                'slug': obj.forked_from.slug,
                'author': obj.forked_from.author.username
            }
        return None


class SnippetCreateUpdateSerializer(serializers.ModelSerializer):
    language_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Snippet
        fields = [
            'title', 'description', 'code', 'language_id',
            'visibility', 'tags'
        ]
    
    def validate_language_id(self, value):
        if not Language.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid language ID")
        return value
    
    def create(self, validated_data):
        language_id = validated_data.pop('language_id')
        language = Language.objects.get(id=language_id)
        snippet = Snippet.objects.create(language=language, **validated_data)
        return snippet
    
    def update(self, instance, validated_data):
        language_id = validated_data.pop('language_id', None)
        
        if language_id:
            instance.language = Language.objects.get(id=language_id)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
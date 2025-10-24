from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_username(self, value):
        """Validate username is unique and meets requirements"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, underscores, and hyphens."
            )
        
        return value
    
    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value.lower()
    
    def validate_password(self, value):
        """Validate password meets Django's requirements"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate password confirmation matches"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    total_followers = serializers.IntegerField(read_only=True)
    total_following = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                 'bio', 'location', 'avatar', 'website', 'github_username',
                 'twitter_username', 'date_joined', 'total_following',
                 'following_count', 'posts_count')
        read_only_fields = ('id', 'date_joined', 'email')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'location', 'website',
                 'github_username', 'twitter_username', 'avatar')
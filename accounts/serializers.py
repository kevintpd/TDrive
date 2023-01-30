from django.contrib.auth import get_user_model, authenticate

from .models import User, RegisterInfo
from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from TDrive.settings import SECRET_KEY
import hashlib

UserModel = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(label='code', max_length=10, write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'code', ]

        extra_kwargs = {
            'root_drive': {'read_only': True},
        }
    def validate(self, attrs):
        code_created = RegisterInfo.objects.filter(email=attrs['email'])
        if code_created.exists():
            if attrs['code'] == hashlib.sha256((attrs['email'] + str(code_created.values()[0].get('create_time')) + SECRET_KEY).encode('utf-8')).hexdigest()[:6].upper():
                del attrs['code']
                return attrs
            raise serializers.ValidationError('Email Validation Code is Wrong')
        else:
            raise serializers.ValidationError('please send email code')


    #这里的模型单独用一个RegisterSerializer，是因为这里有一个验证码，还有一个就是，create的时候密码存储的是明文
    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )
        return user

class UserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'root_drive']
        extra_kwargs = {
            'id': {'read_only': True},
            'email':{'required': True},
            'root_dirve':{'read_only': True}
        }

class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError('inactive_account')
            return attrs
        else:
            raise serializers.ValidationError('invalid_credentials')

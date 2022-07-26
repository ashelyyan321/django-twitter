from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions
from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'id')


class UserSerializerWithProfile(UserSerializer):
   nickname = serializers.CharField(source='profile.nickname')
   avatar_url = serializers.SerializerMethodField()

   def get_avatal_url(self, obj):
       if obj.profile.avatar:
           return obj.profile.avatar.url
       return None

   class Meta:
       model = User
       fields = ('id', 'username', 'nickname', 'avatal_url')


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self,data):
        # User.objects.filter(username__iexact=data['username']),忽略大小写,但一个个效率低
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        #可以多存一份用于展示
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            #password 明文变密文，其他属性做normalize
        )
        user.profile
        return user


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')

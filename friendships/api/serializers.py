from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from friendships.services import FriendshipService
from accounts.services import UserService


class BaseFriendshipSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    has_followed = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def get_user_id(self, obj):
        raise NotImplementedError

    def _get_following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set

    def get_has_followed(self, obj):
        return self.get_user_id(obj) in self._get_following_user_id_set()

    def get_user(self, obj):
        user = UserService.get_user_by_id(self.get_user_id(obj))
        return UserSerializerForFriendship(user).data

    def get_created_at(self, obj):
        return obj.created_at


class FollowingSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.to_user_id


class FollowerSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.from_user_id


#class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
#    user = UserSerializerForFriendship(source='cached_from_user')
#    created_at = serializers.DateTimeField()
#    has_followed = serializers.SerializerMethodField()

 #   class Meta:
 #       model = Friendship
  #      fields = ('user', 'created_at', 'has_followed')

 #   def get_has_followed(self, obj):
        #if self.context['request'].user.is_anonymous:
        #    return False
 #       return obj.from_user_id in self.following_user_id_set
        #每个object都要sql
        #return FriendshipService.has_followed(self.context['request'].user, obj.from_user)


#class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
 ##   user = UserSerializerForFriendship(source='cached_to_user')
 #   created_at = serializers.DateTimeField()
 #   has_followed = serializers.SerializerMethodField()

  #  class Meta:
  #      model = Friendship
  #      fields = ('user', 'created_at', 'has_followed')

   # def get_has_followed(self, obj):
   #     return obj.to_user_id in self.following_user_id_set

      #  if self.context['request'].user.is_anonymous:
      #      return False
        #每个object都要sql
      #  return FriendshipService.has_followed(self.context['request'].user, obj.to_user)


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'do not follow yourself',
            })
        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow non user',
             })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return FriendshipService.follow(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
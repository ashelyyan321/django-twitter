from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = (
            'id',
            'actor_content_type',
            'actor_object_id',
            'verb',
            'action_object_content_type',
            'action_object_object_id',
            'target_content_type',
            'target_object_id',
            'timestamp',
            'unread',
        )


class NotificationSerializerForUpdate(serializers.ModelSerializer):
    unread = serializers.BooleanField()

    #只有unread可以被更新
    class Meta:
        model = Notification
        fields = ('unread',)

    def update(self, instance, validated_date):
        instance.unread = validated_date['unread']
        instance.save()
        return instance


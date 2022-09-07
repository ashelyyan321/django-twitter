from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN
from gatekeeper.models import GateKeeper
from friendships.hbase_models import HBaseFollowing, HBaseFollower

import time


cache = caches['testing'] if settings.TESTING else caches['default']


class FriendshipService(object):

    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()
        #select count 看有无

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
       # key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
       # user_id_set = cache.get(key)
       # if user_id_set is not None:
        #    return user_id_set
        #merlization search, 没有从数据库取通过set存到缓存，object缓存存在进程中，memcache则不会进程结束没而是按淘汰机制
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            friendships = Friendship.objects.filter(from_user_id=from_user_id)
        else:
            friendships = HBaseFollowing.filter(prefix=(from_user_id,))

        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        #cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def get_follow_instance(cls, from_user_id, to_user_id):
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        for follow in followings:
            if follow.to_user_id == to_user_id:
                return follow
        return None

    @classmethod
    def has_followed(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return None

        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).exists()

        instance = cls.get_follow_instance(from_user_id, to_user_id)
        return instance is not None

    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return None

        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            )
        now = int(time.time() * 1000000)
        HBaseFollower.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )
        return HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now,
        )

    @classmethod
    def unfollow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return 0

        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
            # Queryset 的 delete 操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
            # 为什么会出现多种类型数据的删除？因为可能因为 foreign key 设置了 cascade 出现级联
            # 删除，也就是比如 A model 的某个属性是 B model 的 foreign key，并且设置了
            # on_delete=models.CASCADE, 那么当 B 的某个数据被删除的时候，A 中的关联也会被删除。
            # 所以 CASCADE 是很危险的，我们一般最好不要用，而是用 on_delete=models.SET_NULL
            # 取而代之，这样至少可以避免误删除操作带来的多米诺效应。
            deleted, _ = Friendship.objects.filter(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
            ).delete()
            return deleted

        instance = cls.get_follow_instance(from_user_id, to_user_id)
        if instance is None:
            return 0

        HBaseFollowing.delete(from_user_id=from_user_id, created_at=instance.created_at)
        HBaseFollower.delete(to_user_id=to_user_id, created_at=instance.created_at)
        return 1

    @classmethod
    def get_following_count(cls, from_user_id):
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.filter(from_user_id=from_user_id).count()
        followings = HBaseFollowing.filter(prefix=(from_user_id, None))
        return len(followings)


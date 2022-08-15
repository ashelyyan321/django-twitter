from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from utils.redis_helper import RedisHelper
from twitter.cache import NEWSFEEDS_PATTERN
from newsfeeds.tasks import fanout_newsfeeds_main_task


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id)
        #异步任务delay

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_objects(key, newsfeed, queryset)





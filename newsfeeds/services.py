from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from utils.redis_helper import RedisHelper
from twitter.cache import NEWSFEEDS_PATTERN


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        #没有.save 没有存储
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        #bulk create 不触发post_save 的signal，要手动push到cache中
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

        #followers = FriendshipService.get_followers(tweet.user)
        #not allowed for+query
        #for follower in followers:
         #   NewsFeed.objects.create(user=follower, tweet=tweet)

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



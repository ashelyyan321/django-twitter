from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(self, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        #没有.save 没有存储
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        #followers = FriendshipService.get_followers(tweet.user)
        #not allowed for+query
        #for follower in followers:
         #   NewsFeed.objects.create(user=follower, tweet=tweet)



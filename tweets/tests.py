from django.contrib.auth.models import User
from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from datetime import timedelta
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus


class TweetTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.linghu = self.create_user('linghu')
        self.tweet = self.create_tweet(self.linghu, content='Jiuzhang Dafa Hao')

    def test_hours_to_now(self):
        fridamm = User.objects.create_user(username='fridamm')
        tweet = Tweet.objects.create(user=fridamm, content='I am the richest woman')
        tweet.created_at = utc_now()-timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_create_photo(self):
        # 测试可以成功创建 photo 的数据对象
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.linghu,
        )
        self.assertEqual(photo.user, self.linghu)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)

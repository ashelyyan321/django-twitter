from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    from_user_id = models.IntegerField(reverse=True)
    #userid很少做范围查询补灵，不再有序,更均匀
    created_at = models.TimestampField()
    #column key, only rowkey for range search
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')


class HBaseFollower(models.HBaseModel):
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followers'
        row_key = ('to_user_id', 'created_at')
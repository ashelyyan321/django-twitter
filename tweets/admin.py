from django.contrib import admin
from tweets.models import Tweet, TweetPhoto



@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )


@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'tweet',
        'file',
        'has_deleted',
    )
    list_filter = ('status', 'has_deleted')
    date_hierarchy = 'created_at'

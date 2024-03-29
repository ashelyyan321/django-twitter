from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetCreateSerializer,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetCreateSerializer
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action == ['list', 'retrieve']:
            return [AllowAny()]
        return [AllowAny()]

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id=user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={'request': request},
        )
        # 要有queryset = Tweet.objects.all()才能有结果
        return Response(serializer.data)

    def create(self, request):
        serializer = TweetCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )


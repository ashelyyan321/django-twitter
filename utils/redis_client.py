from django.conf import settings
import redis


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        #cls = RedisClient
        if cls.conn:
            return cls.conn
        #建立好tcp链接，短时间不会关
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception('you can npt flush redis in prod')
        conn = cls.get_connection()
        conn.flushdb()
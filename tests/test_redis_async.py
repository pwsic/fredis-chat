# -*- coding: utf-8 -*-
from chat import settings
from chat.app import Redis
from tornado import testing


class TestRedisAsync(testing.AsyncTestCase):

    def test_subscribtion_works(self):
        redis = Redis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

        redis.subscribe('#room1')
        redis.publish('#room1', 'hello #room1 mates')
        redis.listen()

    """
    @tesing.
    def test_unsubscription_works(self):
        pass
    """

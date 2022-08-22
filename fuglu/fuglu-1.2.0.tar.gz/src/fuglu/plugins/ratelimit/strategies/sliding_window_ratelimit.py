# -*- coding: UTF-8 -*-
# -*- coding: UTF-8 -*-
#   Copyright 2009-2022 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# based on the ratelimit plugin in the postomaat project (https://gitlab.com/fumail/postomaat)
# developed by @ledgr
import time
import math
from collections import defaultdict
from datetime import timedelta

from .backendint import BackendInterface
from fuglu.extensions.redisext import RedisPooledConn, ENABLED as REDIS_AVAILABLE, REDIS2

AIOREDIS_AVAILABLE = 0
try:
    import asyncio
    import aioredis
    AIOREDIS_AVAILABLE = 1
    aioConnectionError = aioredis.exceptions.ConnectionError
    aioTimeoutError = aioredis.exceptions.TimeoutError
except ImportError:
    aioConnectionError = ConnectionError
    aioTimeoutError = TimeoutError

STRATEGY = 'sliding-window'
BACKENDS = defaultdict(dict)

__all__ = ['STRATEGY', 'BACKENDS']


""" This strategy is based on the blog post by CloudFlare
https://blog.cloudflare.com/counting-things-a-lot-of-different-things

I hope I got this right

Basically we have two buckets - past and present
When we are calculating the rate, we take percentage of previous bucket
and add the total amount of present bucket.
This way we have quite good approximation of the rate.

This algorithm:
  - requires less memory than sliding-log algorithm
  - doesn't require expensive(?) operation of old data cleanup
    like sliding-log does
  - avoids double-burst problem of fixed ratelimit algorithm
  - BUT is less atomic, so less precise
  - uses more memory than fixed ratelimit algorithm

TODO:
    - add async updates to redis
    - avoid race conditions if any (?)
    - improve performance (?)
"""


if REDIS_AVAILABLE:
    class RedisBackend(BackendInterface):
        def __init__(self, backendconfig):
            super(RedisBackend, self).__init__(backendconfig)
            self.redis_pool = RedisPooledConn(backendconfig)

        def add(self, eventname, ttl=0):
            event_data = {
                b'mitigate': 0,
                b'bucket0': 0,
                b'bucket1': 0,
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            }
            redisconn = self.redis_pool.get_conn()
            pipe = redisconn.pipeline()
            if REDIS2:
                pipe.hmset(eventname, event_data)
            else:
                pipe.hset(eventname, mapping=event_data)
            if isinstance(ttl, float):
                ttl = timedelta(seconds=ttl)
            pipe.expire(eventname, ttl)
            pipe.execute()

        def get_event(self, eventname):
            redisconn = self.redis_pool.get_conn()
            return redisconn.hgetall(eventname)

        def update(self, eventname, event_data):
            redisconn = self.redis_pool.get_conn()
            if REDIS2:
                redisconn.hmset(eventname, event_data)
            else:
                redisconn.hset(eventname, mapping=event_data)

        def set_mitigate(self, eventname, retry_after):
            newval = float(self.now) + float(retry_after)
            print(f"Setting mitigate to: {newval}")
            redisconn = self.redis_pool.get_conn()
            if REDIS2:
                redisconn.hmset(eventname, b'mitigate', newval)
            else:
                #pipe.hset(eventname, mapping=event_data)
                redisconn.hmset(eventname, mapping={b'mitigate': newval})

        def get_buckets(self, timespan):
            """get time buckets where counters are saved
            we have two buckets only, but this formula can generate multiple
            math.floor((time_now / measurement_timespan) / bucket_interval)
            """
            present_bucket = int(math.floor((self.now % (timespan * 2)) / timespan))
            past_bucket = 1 - present_bucket
            return f"bucket{str(present_bucket)}".encode(), f"bucket{str(past_bucket)}".encode()

        def reset_buckets(self, event):
            event.update({
                b'bucket0': 0,
                b'bucket1': 0,
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            })

        def reset_bucket(self, event, bucket):
            event[bucket] = 0

        def increment(self, event, inc: int):
            event[self.present_bucket] = int(event[self.present_bucket]) + inc

        def change_bucket(self, event):
            event.update({
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            })

        def count(self, event, timespan):
            t_into_bucket = self.now - float(event[b'bucket_start_ts'])
            present_b = self.present_bucket # present bucket count
            past_b = self.past_bucket       # past bucket count
            if isinstance(timespan, timedelta):
                timespan = timespan.total_seconds()
            count = float(event[past_b]) * ((timespan - t_into_bucket) / timespan) + float(event[present_b]) # pylint: disable=C0301
            return count

        def check_allowed(self, eventname, limit, timespan, increment):
            self.now = time.time()
            self.present_bucket, self.past_bucket = self.get_buckets(timespan)
            count = -1 # not calculated yet or mitigation is on

            print("check allowed sliding-window")
            event = self.get_event(eventname)
            if not event:
                self.add(eventname, ttl=timespan * 3)
                event = self.get_event(eventname)

            # we are ahead of both bucket timespans
            # so the counters are irrelevant and must be reset
            if float(event[b'bucket_start_ts']) + float(2 * timespan) < self.now:
                self.reset_buckets(event)

            if self.present_bucket != event[b'last_bucket']:
                self.change_bucket(event)
                self.reset_bucket(event, self.present_bucket)
                if isinstance(timespan, float):
                    timespan_timedelta = timedelta(seconds=timespan)
                redisconn = self.redis_pool.get_conn()
                redisconn.expire(eventname, timespan_timedelta * 3)

            if b'mitigate' in event and float(event[b'mitigate']) > self.now:
                self.logger.debug(f"{eventname} mitigate flag is already set, retry in {float(event[b'mitigate']) - self.now}")
                return False, count

            count = self.count(event, timespan) + increment # +1 because we check if we WOULD allow
            # block if it WOULD be larger, equal limit is allowed
            if count > limit:
                try:
                    print("not allowed - process actions!")
                    retry_after = float(timespan) / float(event[self.past_bucket])
                except ZeroDivisionError:
                    # pevious bucket is empty
                    try:
                        retry_after = float(timespan) / count
                    except ZeroDivisionError:
                        retry_after = float(timespan)

                if increment < 0:
                    retry_after = -1

                self.logger.debug(f"{eventname} set mitigate flag, retry_after={retry_after}"
                                  f"{', negative because increment < 0' if increment < 0 else ''}")

                #self.set_mitigate(eventname, retry_after)
                newval = float(self.now) + float(retry_after)
                event[b'mitigate'] = newval

                self.logger.debug(f"{eventname} set mitigate flag, retry_after={retry_after}")
                self.update(eventname, event)
                return False, count

            self.increment(event, inc=increment)
            self.update(eventname, event)

            return True, count

    BACKENDS[STRATEGY]['redis'] = RedisBackend


if AIOREDIS_AVAILABLE:
    class AIORedisBackend(BackendInterface):
        def __init__(self, backendconfig):
            super(AIORedisBackend, self).__init__(backendconfig)
            self.config = backendconfig
            self._redis = None
            self._pool = None

        @property
        async def redis(self):
            if not self._redis:
                self.logger.debug(f"(R!=None:{bool(self._redis)}) Connect to redis: {self.config}")
                if hasattr(aioredis, 'create_redis_pool'):
                    try:
                        loop = asyncio.get_running_loop()
                    except AttributeError:
                        # python 3.6
                        loop = asyncio.get_event_loop()
                    self.logger.debug(f"Got running loop...")
                    self._redis = await aioredis.create_redis_pool(self.config, loop=loop, timeout=3)
                else:
                    # version >= 2
                    self._pool = aioredis.BlockingConnectionPool(timeout=3).from_url(url=self.config)
                    self._redis = await aioredis.StrictRedis(connection_pool=self._pool)
            return self._redis

        async def add(self, eventname, ttl=0):
            success = False
            event_data = {
                b'mitigate': 0,
                b'bucket0': 0,
                b'bucket1': 0,
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            }
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    r = await self.redis
                    try:
                        await r.hmset_dict(eventname, event_data)
                    except AttributeError:
                        # aioredis >= 2.0
                        await r.hset(eventname, mapping=event_data)
                    if isinstance(ttl, float):
                        ttl = timedelta(seconds=ttl)
                    if isinstance(ttl, timedelta):
                        ttl = int(ttl.seconds)
                    await r.expire(eventname, ttl)
                    success = True
                    attempts = 0  # no more attempts
                except (ConnectionError, aioConnectionError, TimeoutError, aioTimeoutError) as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'add' - retry {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'add' {str(e)}")
                except Exception as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'add' - retry: {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'add': {str(e)}", exc_info=e)
            return success

        async def get_event(self, eventname):
            event = None
            success = False
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    r = await self.redis
                    event = await r.hgetall(eventname)
                    success = True
                    attempts = 0  # no more attempts
                except (ConnectionError, aioConnectionError, TimeoutError, aioTimeoutError) as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_event' - retry {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_event' {str(e)}")
                except Exception as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'get_event' - retry: {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'get_event': {str(e)}", exc_info=e)
            return event, success

        async def update(self, eventname, event_data):
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    r = await self.redis
                    try:
                        await r.hmset_dict(eventname, event_data)
                    except AttributeError:
                        # aioredis >= 2.0
                        await r.hset(eventname, mapping=event_data)
                    attempts = 0   # no more attempts
                except (ConnectionError, aioConnectionError, TimeoutError, aioTimeoutError) as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'update' - retry {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'update' {str(e)}")
                except Exception as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'update' - retry: {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'update': {str(e)}", exc_info=e)

        async def set_mitigate(self, eventname, retry_after):
            newval = float(self.now) + float(retry_after)
            self.logger.debug(f"Setting mitigate to: {newval}")

            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    r = await self.redis
                    event_data = {b"mitigate": newval}
                    try:
                        await r.hmset_dict(eventname, event_data)
                    except AttributeError:
                        # aioredis >= 2.0
                        await r.hset(eventname, mapping=event_data)
                    attempts = 0  # no more attempts
                except (ConnectionError, aioConnectionError, TimeoutError, aioTimeoutError) as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'set_mitigate' - retry {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'set_mitigate' {str(e)}")
                except Exception as e:
                    self._redis = None
                    if attempts:
                        self.logger.warning(f"Connection error in 'set_mitigate' - retry: {str(e)}")
                        await asyncio.sleep(0.1)
                    else:
                        self.logger.error(f"Connection error in 'set_mitigate': {str(e)}", exc_info=e)

        def get_buckets(self, timespan):
            """get time buckets where counters are saved
            we have two buckets only, but this formula can generate multiple
            math.floor((time_now / measurement_timespan) / bucket_interval)
            """
            present_bucket = int(math.floor((self.now % (timespan * 2)) / timespan))
            past_bucket = 1 - present_bucket
            return f"bucket{str(present_bucket)}".encode(), f"bucket{str(past_bucket)}".encode()

        def reset_buckets(self, event):
            event.update({
                b'bucket0': 0,
                b'bucket1': 0,
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            })

        def reset_bucket(self, event, bucket):
            event[bucket] = 0

        def increment(self, event, inc: int):
            event[self.present_bucket] = int(event[self.present_bucket]) + inc

        def change_bucket(self, event):
            event.update({
                b'last_bucket': self.present_bucket,
                b'bucket_start_ts': self.now
            })

        def count(self, event, timespan):
            t_into_bucket = self.now - float(event[b'bucket_start_ts'])
            present_b = self.present_bucket # present bucket count
            past_b = self.past_bucket       # past bucket count
            if isinstance(timespan, timedelta):
                timespan = timespan.total_seconds()
            count = float(event[past_b]) * ((timespan - t_into_bucket) / timespan) + float(event[present_b]) # pylint: disable=C0301
            return count

        async def check_allowed(self, eventname, limit, timespan, increment):
            self.now = time.time()
            self.present_bucket, self.past_bucket = self.get_buckets(timespan)
            count = -1 # not calculated yet or mitigation is on

            event, success = await self.get_event(eventname)
            if success and (not event or not b'bucket_start_ts' in event):
                success = await self.add(eventname, ttl=timespan * 3)
                if success:
                    event, success = await self.get_event(eventname)

            if not event:
                self.logger.warning(f'{eventname} failed to get event, bailing out')
                return True, count
            
            if not b'bucket_start_ts' in event:
                self.logger.warning(f'{eventname} event is missing bucket_start_ts, bailing out')
                return True, count

            # we are ahead of both bucket timespans
            # so the counters are irrelevant and must be reset
            if float(event[b'bucket_start_ts']) + float(2 * timespan) < self.now:
                self.reset_buckets(event)

            if self.present_bucket != event[b'last_bucket']:
                self.change_bucket(event)
                self.reset_bucket(event, self.present_bucket)
                if isinstance(timespan, (int, float)):
                    timespan_timedelta = timedelta(seconds=timespan)
                else:
                    timespan_timedelta = timedelta(seconds=0)
                if isinstance(timespan_timedelta, timedelta):
                    timespan_timedelta = int(timespan_timedelta.seconds)
                await (await self.redis).expire(eventname, timespan_timedelta * 3)

            if b'mitigate' in event and float(event[b'mitigate']) > self.now:
                self.logger.debug(f"{eventname} mitigate flag is already set, retry in {float(event[b'mitigate']) - self.now}")
                return False, count

            count = self.count(event, timespan) + increment # +1 because we check if we WOULD allow
            # block if it WOULD be larger, equal limit is allowed
            if count > limit:
                try:
                    print("not allowed - process actions!")
                    retry_after = float(timespan) / float(event[self.past_bucket])
                except ZeroDivisionError:
                    # pevious bucket is empty
                    try:
                        retry_after = float(timespan) / count
                    except ZeroDivisionError:
                        retry_after = float(timespan)

                if increment < 0:
                    retry_after = -1

                self.logger.debug(f"{eventname} set mitigate flag, retry_after={retry_after}"
                                  f"{', negative because increment < 0' if increment < 0 else ''}")
                #self.set_mitigate(eventname, retry_after)
                newval = float(self.now) + float(retry_after)

                event[b'mitigate'] = newval

                self.logger.debug(f"{eventname} set mitigate flag, retry_after={retry_after}")
                await self.update(eventname, event)
                return False, count

            self.increment(event, inc=increment)
            await self.update(eventname, event)

            return True, count

    BACKENDS[STRATEGY]['aioredis'] = AIORedisBackend

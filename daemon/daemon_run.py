#!/usr/bin/env python

import asyncio
import websockets
import logging
import asyncio_redis
import json
import time

from asyncio_redis.exceptions import NotConnectedError
from websockets.exceptions import ConnectionClosed

log = logging.getLogger('websockets.server')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


def info(message):
    log.info('{}: {}'.format(time.time(), message))

def error(message):
    log.error('\033[0;91m{}: {}\033[0m'.format(time.time(), message))


class MessageServer:
    def __init__(self, host=None, port=None, redis_host=None, redis_port=None):
        self.host = host or '0.0.0.0'
        self.port = port or 5678
        self.redis_host = redis_host or '127.0.0.1'
        self.redis_port = redis_port or 6379
        self.redis_pub = None
    
    def run(self):
        start_server = websockets.serve(self.listen, self.host, self.port)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect_redis())
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    async def connect_redis(self):
        self.redis_pub = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)

    async def listen(self, websocket, path):
        info('listen')
        key = 'auth:' + path[1:]
        session_info = await self.redis_pub.get(key)
        if session_info is None:
            error('unauthorized socket connection attempt')
            return

        await self.redis_pub.delete([key])

        session = json.loads(session_info)
        user_id = session['user_id']
        channel_id = session['channel_id']
        channel_key = 'channel:' + str(channel_id)

        info('session: {}'.format(session))

        redis_sub = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)
        subscriber = await redis_sub.start_subscribe()
        await subscriber.subscribe([channel_key])

        self.loop.create_task(self.get_messages(subscriber, websocket))

        while True:
            try:
                message = await websocket.recv()
            except ConnectionClosed:
                info('connection closed')
                break

            info('received: {}'.format(message))
            envelope = {
                'ts': time.time(),
                'user_id': user_id,
                'channel_id': channel_id,
                'text': message
            }
            info('publishing: {}'.format(envelope))
            await self.redis_pub.publish(channel_key, json.dumps(envelope))

    async def get_messages(self, subscriber, websocket):
        try:
            if websocket.open:
                incoming = await subscriber.next_published()
                info('sending back: [{}] {}'.format(id(websocket), incoming.value))
                await websocket.send(incoming.value)
                self.loop.create_task(self.get_messages(subscriber, websocket))
        except ConnectionClosed:
            error('websocket closed: [{}] {}'.format(id(websocket), incoming.value))
          


def main():
    server = MessageServer()
    server.run()


if __name__ == '__main__':
    main()
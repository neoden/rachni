#!/usr/bin/env python

import asyncio
import websockets
import logging
import asyncio_redis
import json


logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MessageServer:
    def __init__(self, host=None, port=None, redis_host=None, redis_port=None):
        self.host = host or '0.0.0.0'
        self.port = port or 5678
        self.redis_host = redis_host or '127.0.0.1'
        self.redis_port = redis_port or 6379
        self.redis = None
    
    def run(self):
        start_server = websockets.serve(self.listen, self.host, self.port)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect_redis())
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    async def connect_redis(self):
        self.redis_pub = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)
        print(id(self.redis_pub))

    async def listen(self, websocket, path):
        session_info = await self.redis_pub.get(path[1:])
        session = json.loads(session_info)
        user_id = session['user_id']
        channel_id = session['channel_id']

        redis_sub = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)
        subscriber = await redis_sub.start_subscribe()
        await subscriber.subscribe([channel_id])

        while True:
            self.loop.create_task(self.get_messages(subscriber, websocket))
            message = await websocket.recv()
            if message is None:
                break
            print(message)
            #await 
            await self.redis_pub.publish(channel_id, message)

    async def get_messages(self, subscriber, websocket):
        incoming = await subscriber.next_published()
        self.loop.create_task(self.get_messages(subscriber, websocket))
        # echo
        await websocket.send(incoming.value)


def main():
    server = MessageServer()
    server.run()


if __name__ == '__main__':
    main()
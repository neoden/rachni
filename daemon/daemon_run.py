#!/usr/bin/env python

import asyncio
import websockets
import logging
import asyncio_redis


logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MessageServer:
    def __init__(self, host=None, port=None, redis_host=None, redis_port=None):
        self.host = host or '127.0.0.1'
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
        self.redis = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)

    async def listen(self, websocket, path):
        while True:
            message = await websocket.recv()
            if message is None:
                break
            await websocket.send(message)


def main():
    server = MessageServer()
    server.run()


if __name__ == '__main__':
    main()
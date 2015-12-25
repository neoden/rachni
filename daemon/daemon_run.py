#!/usr/bin/env python

import asyncio
import websockets
import logging


logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class MessageServer:
    def __init__(self, host, port, redis_uri):
        self.host = host
        self.port = port
        self.redis_uri = redis_uri
    
    def run(self):
        start_server = websockets.serve(self.listen, self.host, self.port)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()

    async def listen(self, websocket, path):
        await self.on_connect(websocket, path)
        
        while True:
            message = await websocket.recv()
            if message is None:
                await self.on_disconnect(websocket, path)
                break
            await self.on_message(websocket, path, message)

    async def on_message(self, websocket, path, message):
        await websocket.send(message)

    async def on_connect(self, websocket, path):
        print('Connect: {}'.format(path))

    async def on_disconnect(self, websocket, path):
        print('Disconnect: {}'.format(path))


def main():
    server = MessageServer('127.0.0.1', 5678, '')
    server.run()


if __name__ == '__main__':
    main()
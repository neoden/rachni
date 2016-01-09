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


def debug(message):
    log.debug('\033[0;33m{}: {}\033[0m'.format(time.time(), message))

def info(message):
    log.info('{}: {}'.format(time.time(), message))

def error(message):
    log.error('\033[0;91m{}: {}\033[0m'.format(time.time(), message))


def key(prefix, name):
    return '{}:{}'.format(prefix, str(name))


class Session:
    def __init__(self):
        self.message_task = None

    @property
    def channel_id(self):
        return self.current_channel['id']

    @property
    def user_id(self):
        return self.user['id']
        
    async def create(self, session_info, server, websocket):
        for k, v in session_info.items():
            setattr(self, k, v)
        self.server = server
        self.websocket = websocket
        self.redis_sub = await asyncio_redis.Connection.create(
                                    host=server.redis_host, 
                                    port=server.redis_port)
        self.subscriber = await self.redis_sub.start_subscribe()
        await self.subscriber.subscribe([key('channel', c['id']) for c in self.channels])
        await self.schedule()

    async def close(self):
        debug('closing session')
        self.redis_sub.close()
        if self.websocket:
            await self.websocket.close()
        if self.message_task:
            self.message_task.cancel()
        debug('session closed')

    async def get_messages(self):
        try:
            incoming = await self.subscriber.next_published()
            info('sending back: {}'.format(incoming.value))
            await self.websocket.send(incoming.value)
            await self.schedule()
        except ConnectionClosed:
            await self.close()
        except asyncio.CancelledError:
            debug('message task cancelled')

    async def schedule(self):
        debug('scheduling message task')
        self.message_task = self.server.loop.create_task(self.get_messages())

    def __repr__(self):
        return 'Session <User: {}, Channel: {}>'.format(self.user_id, self.channel_id)


class MessageServer:
    def __init__(self, host=None, port=None, redis_host=None, redis_port=None):
        self.host = host or '0.0.0.0'
        self.port = port or 5678
        self.redis_host = redis_host or '127.0.0.1'
        self.redis_port = redis_port or 6379
        self.redis_pub = None
    
    def run(self):
        self.loop = asyncio.get_event_loop()
        debug('starting server')
        self.loop.run_until_complete(asyncio.gather(
            self.connect_redis(),
            websockets.serve(self.listen, self.host, self.port)))
        debug('entering loop')
        self.loop.run_forever()

    async def connect_redis(self):
        self.redis_pub = await asyncio_redis.Connection.create(host=self.redis_host, port=self.redis_port)

    async def authenticate(self, path):
        auth_key = key('auth', path[1:])
        session_info = await self.redis_pub.get(auth_key)
        if session_info is None:
            error('unauthorized socket connection attempt')
            return None
        await self.redis_pub.delete([auth_key])
        return session_info

    async def listen(self, websocket, path):
        debug('incoming websocket connection')
        session_info = await self.authenticate(path)
        if not session_info:
            return

        session = Session()
        await session.create(json.loads(session_info), self, websocket)

        info('session: {}'.format(session))

        while True:
            try:
                message = await websocket.recv()
            except ConnectionClosed:
                debug('connection closed')
                await session.close()
                break

            info('received: {}'.format(message))
            envelope = {
                'ts': time.time(),
                'user_id': session.user_id,
                'channel_id': session.channel_id,
                'text': message
            }
            info('publishing: {}'.format(envelope))
            await self.redis_pub.publish(key('channel', session.channel_id), json.dumps(envelope))


def main():
    server = MessageServer()
    server.run()


if __name__ == '__main__':
    main()
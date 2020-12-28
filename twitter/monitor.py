
import json
import tweepy
import shelve
from queue import Queue
from asyncio import sleep, new_event_loop
import asyncio
import logging
import re
from time import strptime, strftime, struct_time
from datetime import datetime as dt, timedelta
from pprint import pprint
import aiohttp
from discord import Webhook, AsyncWebhookAdapter, Embed
from urllib3.exceptions import ProtocolError
from http.client import IncompleteRead


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)


class UserStream(tweepy.StreamListener):
    def __init__(self, config, queue, extendedQueue):
        super().__init__()
        self.config = config
        self.queue = queue
        self.extendedQueue = extendedQueue
        self.count = 0
        self.truncated = 0
        self.loop = new_event_loop()

    @staticmethod
    def getTime(created):
        data = created.split(' ')
        monthNumber = int(strptime(data[1], '%b').tm_mon)
        day = int(data[2])
        time = data[3].split(':')
        hours = int(time[0])
        minutes = int(time[1])
        year = int(data[-1])
        finalTime = dt(year, monthNumber, day, hours,
                       minutes) - timedelta(hours=5)
        new = finalTime.strptime(
            f'{finalTime.hour}:{finalTime.minute}', "%H:%M")
        new = new.strftime("%I:%M %p")
        final = f'{new} {finalTime.year}-{finalTime.month}-{finalTime.day}'
        return final

    def on_status(self, status):
        self.count += 1
        if status._json['truncated']:
            self.extendedQueue.put(status)
            self.truncated += 1
            return
        # print(f'Total : {self.count}, Truncated : {self.truncated}')
        # pprint(status._json)
        self.queue.put(status)

    def on_error(self, error):
        print('error found!')
        print(error)

    def on_disconnect(self, notice):
        print('Disconnect notice')
        print(notice)

    def on_exception(self, exception):
        print('Restarting the stream ..')
        return True


class Monitor:
    def __init__(self, filterQueue, extendedQueue):
        f = open('config.json', 'r')
        self.config = json.load(f)
        self.trackList = list(self.config.get("SET1"))
        auth = tweepy.OAuthHandler(self.config.get(
            'TWITTER_API_KEY'), self.config.get('TWITTER_API_KEY_SECRET'))
        auth.set_access_token(self.config.get(
            "ACCESS_TOKEN"), self.config.get('ACCESS_TOKEN_SECRET'))
        self.api = tweepy.API(auth)
        self.loop = new_event_loop()
        self.extendedQueue = extendedQueue
        self.filterQueue = filterQueue

    def start(self):
        self.loop.run_until_complete(self.main())

    async def extendedQueueHandler(self):
        print('Extended queue hanfler running ..')
        while True:
            status = self.extendedQueue.get()
            print('Partial status obj')
            pprint(status._json)
            fullStatus = self.api.get_status(status._json['id'])
            print('Got a full status ...')
            pprint(fullStatus._json)

    async def main(self):
        await self.startStream()
        # await self.waitForTweets()

    async def getHomeTimeLine(self):
        timeline = self.api.home_timeline()
        return timeline

    async def getUserID(self, user):
        user = self.api.get_user(user)
        return user._json.get('id_str')

    async def startStream(self):
        listener = UserStream(
            self.config, self.filterQueue, self.extendedQueue)
        stream = tweepy.Stream(auth=self.api.auth, listener=listener)

        async def restartStream():
            print(" Starting the twitter stream ...")
            try:
                stream.filter(track=self.trackList,
                              languages=['en'])
                print(' Twitter stream started!')
            except ProtocolError:
                await restartStream()
            except IncompleteRead:
                await restartStream()
        await restartStream()

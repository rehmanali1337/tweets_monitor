
import tweepy
import json
from asyncio import new_event_loop
from pprint import pprint


class Helper:
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

    async def main(self):
        print(' Helper Thread Running ..')
        while True:
            status = self.extendedQueue.get()
            print('Partial status obj')
            pprint(status._json)
            fullStatus = self.api.get_status(status._json['id'])
            print('\n\n\n')
            print('Got a full status ...')
            pprint(fullStatus._json)

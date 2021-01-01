import asyncio
import aiohttp
from discord import Webhook, AsyncWebhookAdapter, Embed
from pprint import pprint


class FilterTweets:
    def __init__(self, name, tweetsQueue, dbQueue, set1, set2, set3, webhook):
        self.tweetsQueue = tweetsQueue
        self.dbQueue = dbQueue
        self.name = name
        self.set1 = list(set1)
        self.set2 = list(set2)
        self.set3 = list(set3)
        self.webhook = webhook
        self.loop = asyncio.new_event_loop()

    def start(self):
        self.loop.run_until_complete(self.main())

    async def main(self):
        while True:
            status = self.tweetsQueue.get()
            set1Found = False
            set2Found = False
            set3Found = False
            # pprint(status._json)
            text = status._json['text']
            if status._json['truncated']:
                print('Truncated tweet found!')
                text = status._json['extended_tweet']['full_text']
            user = status._json['user']['name']
            me = False
            if user == 'Rehman Ali':
                print('Tweet from me!')
                me = True
                # exit()
            for w in self.set1:
                if w.lower() in text.lower():
                    set1Found = True
                    if me:
                        print('Set 1 passed!')
            for w in self.set2:
                if w.lower() in text.lower():
                    set2Found = True
                    if me:
                        print('Set 2 passed!')
            for w in self.set3:
                if w.lower() in text.lower():
                    set3Found = True
                    if me:
                        print('Set 3 passed!')
            if '$' in text:
                set3Found = True
                if me:
                    print('$ passed!')

            def createWords(text):
                sublists = [s for s in text.split('\n')]
                words = []
                for l in sublists:
                    finalList = l.split(' ')
                    words.extend([w for w in finalList])
                words = list(filter(None, words))
                string = ' '.join(words)
                words = ''.join(
                    ch for ch in string if ch.isalnum() or ch == ' ')
                return [w for w in words.split(' ')]

            words = createWords(text)
            for w in words:
                if me:
                    print(w)
                if len(w) <= 4 and len(w) >= 1:
                    if me:
                        print('Length match')
                    if w.isupper():
                        if me:
                            print("All uper")
                        set3Found = True
            if set1Found and set2Found and set3Found:
                print('Tweet Matched')
                await self.sendToDiscord(status)
            self.tweetsQueue.task_done()

    async def sendToDiscord(self, status):
        # pprint(status._json)
        self.dbQueue.put(status)
        text = status._json.get('text')
        embed = Embed(title='New Tweet')
        embed.add_field(
            name='Author', value=status._json['user']['name'], inline=False)
        embed.add_field(
            name='Tweet URL', value=f'https://twitter.com/i/web/status/{status._json.get("id")}')
        embed.description = text
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(
                self.webhook, adapter=AsyncWebhookAdapter(session))
            await webhook.send(embed=embed, username='Twitter')
        print('Tweet sent to discord!')

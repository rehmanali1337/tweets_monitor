from twitter.tweetsMonitor import Monitor
from utils.db import DB
import asyncio
import json
from queue import Queue
from twitter.tweetsMonitor import Monitor
from utils.db import DB
import threading
from utils.filterThread import FilterTweets
from utils.helperThread import Helper


def main():
    f = open('config.json', 'r')
    config = json.load(f)
    dbQueue = Queue()
    db = DB(dbQueue)
    tweetsQueue = Queue()
    extendedQueue = Queue()
    # helper = Helper(tweetsQueue, extendedQueue)
    monitor = Monitor(tweetsQueue, extendedQueue)
    threading.Thread(target=db.start, name='Database Thread').start()
    threading.Thread(target=monitor.start, name='Monitor Thread').start()
    # threading.Thread(target=helper.start).start()
    for i in range(2000):
        filteringThread = FilterTweets(f'Filter {i}', tweetsQueue, dbQueue, config.get("SET1"),
                                       config.get("SET2"), config.get("SET3"),
                                       config.get("DISCORD_CHANNEL_WEBHOOK"))
        threading.Thread(target=filteringThread.start,
                         name=f'Tweets Filter Thread {i}').start()
    print(' Bot is up!')


if __name__ == "__main__":
    main()

import asyncio
import json
from queue import Queue
from twitter.monitor import Monitor
from utils.db import DB
import threading
from utils.filterThread import FilterTweets
from utils.helperThread import Helper
import argparse


def main():
    f = open('config.json', 'r')
    config = json.load(f)
    dbQueue = Queue()
    db = DB(dbQueue)
    tweetsQueue = Queue()
    extendedQueue = Queue()
    monitor = Monitor(tweetsQueue, extendedQueue)
    threading.Thread(target=db.start, name='Database Thread').start()
    threading.Thread(target=monitor.start, name='Monitor Thread').start()
    for i in range(500):
        filteringThread = FilterTweets(f'Filter {i}', tweetsQueue, dbQueue, config.get("SET1"),
                                       config.get("SET2"), config.get("SET3"),
                                       config.get("DISCORD_CHANNEL_WEBHOOK"))
        threading.Thread(target=filteringThread.start,
                         name=f'Tweets Filter Thread {i}').start()
    print(' Bot is up!')


if __name__ == "__main__":
    main()

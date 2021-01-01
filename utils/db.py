import asyncio
import mysql.connector as connector
import queue
from datetime import datetime as dt
import json


class DB:
    def __init__(self, queue):
        f = open('config.json', 'r')
        self.config = json.load(f)
        self.queue = queue
        self.loop = asyncio.new_event_loop()
        self.databaseName = self.config.get("DATABASE_NAME")
        self.tableName = self.config.get("TABLE_NAME")

    def start(self):
        def connection():
            config = {
                "user": self.config.get("DATABASE_USERNAME"),
                "password": self.config.get("DATABASE_PASSWORD"),
                "host": self.config.get("MYSQL_SERVER_ADDRESS"),
                "port": 3306,
                'database': self.databaseName
            }
            # try:
            c = connector.connect(**config)
            return c
            # except:
            # print("connection error")
            # exit(1)

        cn = connection()
        cur = cn.cursor()
        cur.execute("select version();")
        print(f' Using database version : {cur.fetchone()}')
        self.loop.run_until_complete(self.main(cur))

    async def createTableIfNotExists(self, cur):
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {self.tableName} (user VARCHAR(255), timestamp VARCHAR(255), content VARCHAR(1000))")

    async def createDatabaseIfNotExists(self, cur):
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.databaseName};")

    async def main(self, cur):
        await self.createDatabaseIfNotExists(cur)
        await self.createTableIfNotExists(cur)
        while True:
            status = self.queue.get()
            username = status._json.get("user")['screen_name']
            date = dt.fromtimestamp(int(status._json.get("timestamp_ms"))/1000)
            timestamp = f'{date.year}/{date.month}.{date.day}'
            content = status._json.get("text")
            statement = f'INSERT INTO {self.tableName}(user, timestamp, content) VALUES (%s, %s, %s)'
            cur.execute(statement, (username, timestamp, content))
            self.queue.task_done()

from enum import Enum
import asyncio
import aiohttp
from time import time


class Services(Enum):
    UPS = 'UPS'
    USPS = 'USPS'


def write_image(data):
    filename = f'file-{int(time() * 1000)}.jpeg'
    with open(filename, 'wb') as f:
        f.write(data)


async def fetch_content(url, session):
    async with session.get(url, allow_redirects=True) as response:
        data = await response.read()
        write_image(data)


async def main2():
    print('Start back task')
    url = 'https://loremflickr.com/320/240'
    tasks = []
    while True:
        async with aiohttp.ClientSession() as session:
            for i in range(2):
                task = asyncio.create_task(fetch_content(url, session))
                tasks.append(task)

            await asyncio.gather(*tasks)
        print('File has been downloaded, sleep for 2 seconds')
        await asyncio.sleep(2)


async def start_background_tasks(app):
    app['cats_downloaded'] = asyncio.create_task(main2())


async def stop_background_tasks(app):
    app['cats_downloaded'].cancel()
    await app['cats_downloaded']


import asyncio
import aiohttp
import html5lib
from bs4 import BeautifulSoup
import re

from db import Urls, Connections, session, insert


IMAGES = ('.jpg', '.png', '.gif')
D = 1
START_LINK = 'https://ru.wikipedia.org/wiki/DWDM'

urls_queue = asyncio.Queue()
urls_queue.put_nowait(START_LINK)


async def get_site(u_q):
    global D
    D += 1
    url = await u_q.get()
    while D < 7:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.read()
                await get_urls(text, u_q, url)
                u_q.task_done()
        break


async def get_urls(html, u_q, parent_url):
    soup = BeautifulSoup(html, features="html5lib")
    content_divs = soup.findAll('div', attrs={'id': 'mw-content-text'})
    for div in content_divs:
        all_links = div.findAll('a', attrs={'href': re.compile("^/wiki/")})
        for link in all_links:
            t = str(link.get('href'))
            wiki_url = 'https://ru.wikipedia.org' + t
            if not t.endswith(IMAGES):
                u_q.put_nowait(wiki_url)
                # print("Link -- %s \n Parent -- %s \n Depth -- %s\n\n\n" % (wiki_url, parent_url, D))
    await get_site(urls_queue)


async def main():
    while not urls_queue.empty():
        await get_site(urls_queue)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

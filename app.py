import asyncio
import aiohttp
import html5lib
from bs4 import BeautifulSoup
import re



IMAGES = ('.jpg', '.png', '.gif')
D = 0
task = ['https://ru.wikipedia.org/wiki/DWDM', ]

queue = asyncio.Queue()
queue.put_nowait('https://ru.wikipedia.org/wiki/DWDM')


async def get_site_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            global D
            D += 1
            text = await resp.read()
        soup = BeautifulSoup(text, features="html5lib")
        content_divs = soup.findAll('div', attrs={'id': 'mw-content-text'})
        for div in content_divs:
            all_links = div.findAll('a', attrs={'href': re.compile("^/wiki/")})
            for link in all_links:
                t = str(link.get('href'))
                wiki_url = 'https://ru.wikipedia.org' + t
                if not t.endswith(IMAGES) and wiki_url not in task:
                    task.append(wiki_url)
                    # queue.put_nowait(wiki_url)
                    # print(wiki_url, D, '\n')
        print(len(task))


async def foo(loop):
    global D
    while D < 7:
        while task:
            await get_site_content(task.pop())
            # print(task)
        # await asyncio.sleep(5)
        return (await foo(loop))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(foo(loop))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
"""
loop = asyncio.get_event_loop()
while D < 7:
    sites_soup = loop.run_until_complete(get_site_content(SELECTED_URL, D))
    print(sites_soup)
    print('stop')
loop.close()
"""
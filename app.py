import asyncio
import aiohttp
import html5lib
from bs4 import BeautifulSoup
import re


SELECTED_URL = 'https://ru.wikipedia.org/wiki/DWDM'
IMAGES = ('.jpg', '.png', '.gif')
D = 0
seen_sites = []
task = []


async def get_site_content(url, dept):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.read()
        soup = BeautifulSoup(text, features="html5lib")
        urls = []
        content_divs = soup.findAll('div', attrs={'id': 'mw-content-text'})
        for div in content_divs:
            all_links = div.findAll('a', attrs={'href': re.compile("^/wiki/")})
            for link in all_links:
                t = str(link.get('href'))
                if not t.endswith(IMAGES):

                    print(t, '\n')
    return urls

loop = asyncio.get_event_loop()
while D < 7:
    sites_soup = loop.run_until_complete(get_site_content(SELECTED_URL, D))
    print(sites_soup)
    print('stop')
loop.close()

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

from db import Urls, Connections, session
from config import IMAGES, START_LINK, MAX_PAGES

HTML_PAGE_COUNT = 1  # visiting page count, first -- start page

session.add(Urls(START_LINK, HTML_PAGE_COUNT))  # add start url to db
session.commit()

urls_queue = asyncio.Queue()   # create queue
urls_queue.put_nowait(START_LINK)  # add start url to queue


async def get_site(u_q):
    """
    Get html page from url in queue
    :param u_q: queue of urls to parse
    """

    global HTML_PAGE_COUNT
    HTML_PAGE_COUNT += 1
    url = await u_q.get()
    while HTML_PAGE_COUNT < MAX_PAGES:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as resp:
                text = await resp.read()
                await get_urls(text, u_q, url)
                u_q.task_done()
        break


async def get_urls(html, u_q, parent_url):
    """
    Crawl urls from main context div of wiki article
    :param html: full html page of current article
    :param u_q: urls queue
    :param parent_url: parent article
    """

    soup = BeautifulSoup(html, features="html5lib")
    content_divs = soup.findAll('div', attrs={'id': 'mw-content-text'})
    for div in content_divs:
        all_links = div.findAll('a', attrs={'href': re.compile("^/wiki/")})
        for link in all_links:
            t = str(link.get('href'))
            wiki_url = 'https://ru.wikipedia.org' + t
            if not t.endswith(IMAGES):
                u_q.put_nowait(wiki_url)
                session.add(Urls(wiki_url, HTML_PAGE_COUNT))
                session.commit()
                url_id = session.query(Urls.id).filter_by(url=parent_url)
                page_id = session.query(Urls.id).filter_by(url=wiki_url)
                session.add(Connections(url_id, page_id))
                session.commit()
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

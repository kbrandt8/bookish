import asyncio

import aiohttp


class Search:
    def __init__(self, url_set, obj_format):
        self.results_raw = []
        self.results = []
        self.url_set = url_set
        self.obj_format = obj_format
        asyncio.run(self.start())

    async def start(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.search(session,url) for url in self.url_set]
            await asyncio.gather(*tasks)
            if callable(self.obj_format):
                self.results = [
                    book
                    for r in self.results_raw
                    for book in self.obj_format(r)
                ]



    async def search(self, session,url):
        try:
            async with session.get(url, timeout=8) as res:
                data = await res.json()
                self.results_raw.append(data)
        except Exception as e:
            print(f"Error fetching: {e}")
            return

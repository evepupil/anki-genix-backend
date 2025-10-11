import asyncio
from crawl4ai import *

async def crawl_web_content(url, type):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
    if type == "markdown":
        return(result.markdown)
    return result.json


if __name__ == "__main__":
    url = "https://blog.csdn.net/weixin_44840899/article/details/135659524"
    type = "markdown"
    result = asyncio.run(crawl_web_content(url, type))
    print(result)
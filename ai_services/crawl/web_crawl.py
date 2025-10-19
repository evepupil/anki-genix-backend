import asyncio
import yaml
import os
from crawl4ai import *

def load_crawl_prompts():
    """
    加载网页爬取提示词配置文件

    Returns:
        dict: 提示词配置字典
    """
    prompts_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'prompts',
        'prompts_web_crawl.yaml'
    )

    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_extraction_instruction(mode='learning_content', lang='zh'):
    """
    获取内容提取指令

    Args:
        mode: 提取模式 (learning_content/concise/full)
        lang: 语言 (zh/en/ja)

    Returns:
        str: 提取指令文本
    """
    prompts = load_crawl_prompts()
    try:
        return prompts['web_content_extraction'][mode][lang]['instruction']
    except KeyError:
        # 默认返回中文学习内容模式
        return prompts['web_content_extraction']['learning_content']['zh']['instruction']

async def crawl_web_content(url, type='markdown', mode='learning_content', lang='zh'):
    """
    爬取网页内容

    Args:
        url: 网页URL
        type: 返回类型 (markdown/json)
        mode: 提取模式 (learning_content/concise/full)
        lang: 语言 (zh/en/ja)

    Returns:
        str: 提取的内容（markdown格式）或 JSON
    """
    # 获取提取指令
    extraction_instruction = get_extraction_instruction(mode, lang)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            # 可以传入提取指令给 crawl4ai（如果支持的话）
            # extraction_strategy=LLMExtractionStrategy(instruction=extraction_instruction)
        )

    if type == "markdown":
        return result.markdown
    return result.json


if __name__ == "__main__":
    url = "https://blog.csdn.net/weixin_44840899/article/details/135659524"
    type = "markdown"
    mode = "learning_content"  # 可选: learning_content, concise, full
    lang = "zh"  # 可选: zh, en, ja

    result = asyncio.run(crawl_web_content(url, type, mode, lang))
    print(result)
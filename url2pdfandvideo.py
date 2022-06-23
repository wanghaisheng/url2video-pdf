

#!/usr/bin/env python3
# areq.py

"""Asynchronously get links embedded in multiple pages' HMTL."""

import asyncio
import logging
import re
import sys
from typing import IO
import urllib.error
import urllib.parse
import os,subprocess
import aiofiles
from os.path import isfile, join

import aiohttp
from aiohttp import ClientSession

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

useragent = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
]




async def print_one(pdfpath: IO, url: str, **kwargs) -> None:
    """Write the found HREFs from `url` to `file`."""
    print('url',url)
    pdfname=url.split('/')[-1]
    # print(url)

    if not os.path.exists(join(pdfpath,pdfname+'.pdf')):
        # os.chdir(pdfpath)
        pdfname=join(pdfpath,pdfname+'.pdf')
        # cmd=f'shot-scraper pdf {url} -o {pdfname}'
        cmd=f'python playwright_pdf.py --url {url} --pdf {pdfname}'
        print(cmd)
        isdone=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = isdone.communicate()

        if isdone.returncode == 0 and os.path.exists(join(pdfpath,pdfname+'.pdf')):
            print("url to pdf Job done.")
        else:
            print("url to pdf ERROR",err)
            print(out)    
    else:
        print('pdf dir  is here',pdfpath)


async def bulk_pdf(pdfpath: IO, urls: set, **kwargs) -> None:
    """Crawl & write concurrently to `file` for multiple `urls`."""
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                print_one(pdfpath=pdfpath, url=url, session=session, **kwargs)
            )
        await asyncio.gather(*tasks)
def list_split(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]

if __name__ == "__main__":
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires Python 3.7+."
    here = pathlib.Path(__file__).parent
    post_urls=[]
    product_urls=[]
    forum_urls=[]
    article_urls=[]
    group_urls=[]
    interview_urls=[]
    urls=[]
    keywords=['interview','post','product','forum','article','group']
    links=[]
    outdir = here.joinpath('data/')
    # keyword='post'
    # asyncio.run(bulk_pdf(pdfpath=outdir.joinpath(keyword), urls=urls[]))

    with open(here.joinpath("indiehackers.txt")) as infile:
        links = set(map(str.strip, infile))
    print(len(links))
    for keyword in keywords:    
        for i in links:
            if '/'+keyword+'/' in i:
                urls.append(i)
        print(outdir)
        if not  os.path.exists(outdir):
            print('prepare data dir',outdir)
            os.mkdir(outdir)

        if not os.path.exists(outdir.joinpath(keyword)):
            os.mkdir(outdir.joinpath(keyword))
    newurls=list_split(urls,500)
    for idx,item in enumerate(newurls):
        print(len(item))
        print(item[:1])
        asyncio.run(bulk_pdf(pdfpath=outdir.joinpath(keyword), urls=item))
        # 压缩视频文件
        outdir = here.joinpath('data/')
        # zipdir=outdir.joinpath(keyword)
        os.chdir(outdir)
        # os.system(f'rar a  {keyword}-{str(idx)}.rar {keyword}')
        os.system(f'zip -r -s 1g {keyword}.zip {keyword}/')
        # 删除视频文件
        # os.remove(here.joinpath(f'data/{keyword}'))
        os.chdir('..')




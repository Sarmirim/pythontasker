
from aiohttp import ClientSession, TCPConnector
import asyncio
import sys
import pypeln as pl


limit = 1000
urls = ("http://localhost:8080/{}".format(i) for i in range(int(sys.argv[1])))


async def main():

    async with ClientSession(connector=TCPConnector(limit=0)) as session:

        async def fetch(url):
            async with session.get(url) as response:
                return await response.read()

        await pl.task.each(
            fetch, urls, workers=limit,
        )


asyncio.run(main())




async def make_requests(list):
    async with ClientSession() as session:
        tasks = []
        for prox in list:
            tasks.append(check(prox, session=session))
        results = await asyncio.gather(*tasks)

async def check(prox: str, session: ClientSession):
    try:
        async with session.get('http://142.93.171.79:3000/test', proxy=prox, timeout=30) as response:
            print(await response.json())
        # r = requests.get('http://142.93.171.79:3000/test', proxies=opts, timeout=10)
        # r.status_code
    except aiohttp.ServerDisconnectedError as SDE:
        print(SDE)
    except TimeoutError as TE:
        print(TE)
    except ClientConnectionError as CCE:
        print(CCE.host)
        print(CCE.strerror)
    except TimeoutError as TE:
        print("TIMEOUT")
    except asyncio.exceptions.TimeoutError as TE:
        print("TIMEOUT")
    except ContentTypeError as CTE:
        print("ContentTypeError")
    except Exception as error:       
        print(error)
        print(type(error))
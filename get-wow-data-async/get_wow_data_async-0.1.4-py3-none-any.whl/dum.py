from getwowdataasync.helpers import *
from getwowdataasync import WowApi
from pprint import pprint
from time import perf_counter
from asyncio import Semaphore

async def x():
    start = perf_counter()
    api = await WowApi.create('us')
    json = await api.item_search(**{"id": f"({0},)", "orderby": "id", "_pageSize": 1000})
    end = perf_counter()
    print(f'total time: {end-start}')
    await api.close()
    #pprint((json))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(x())
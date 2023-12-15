import asyncio
from bd_connect import get_all_names, reset_user_name_all_events
from reload_events import reload_profile_events


async def reload_database():
    names = await get_all_names()
    semaphore = asyncio.Semaphore(3)

    async def process(name, index):
        async with semaphore:
            await reset_user_name_all_events(name,index)
            await reload_profile_events(name, 0, index)

    tasks = [process(name, index) for name, index in names]
    await asyncio.gather(*tasks)

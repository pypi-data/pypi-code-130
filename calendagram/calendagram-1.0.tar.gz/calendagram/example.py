import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Text
from calendagram import DateManager, DatetimeManager

token = '5084243247:AAEdUTUir-QcSJitzvNx39ktAqOotOE_WtM'

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())


async def get_date(call: types.CallbackQuery):
    await call.message.answer(text=str(dm.get_date(call_data=call.data)))


async def get_datetime(msg: types.Message, state: FSMContext):
    await msg.answer(text=str(await dtm.get_datetime(text=msg.text, state=state)))

dm = DateManager(router=dp, callback=get_date, open_on_filter=Text(text='/date'))
dtm = DatetimeManager(router=dp, callback=get_datetime, open_on_filter=Text(text='/datetime'))

asyncio.run(dp.run_polling(bot))
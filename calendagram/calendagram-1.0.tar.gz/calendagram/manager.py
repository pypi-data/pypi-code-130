import typing
from datetime import date, datetime
from aiogram import Router, types
from aiogram.filters import Text, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from calendagram.keyboards import date_kb, cancel_kb


class TimeManagersStates(StatesGroup):
    DatetimeGetter = State()


class DateManager:

    def __init__(self, router: Router, callback: typing.Awaitable, open_on_filter: BaseFilter):
        self._router = router
        self._callback = callback
        self._filter = open_on_filter

        self._router.message.register(self._show_calendar, self._filter, state='*')
        self._router.callback_query.register(self._show_date, Text(text_startswith='show_date'))
        self._router.callback_query.register(self._it_is, Text(text_startswith='it_is_'))
        self._router.callback_query.register(self._cancel, Text(text='cancel_op'))
        self._register()

    @classmethod
    def get_prefix(cls):
        return cls.__name__ + '_'

    @classmethod
    def get_date(cls, call_data: str):
        year, month, day = list(map(int, call_data.replace(cls.get_prefix(), '').split('_')))
        return date(year=year, month=month, day=day)

    @staticmethod
    async def _it_is(call: types.CallbackQuery):
        data = {'year': '⚠ Эта кнопка лишь показывает год!',
                'month': '⚠ Эта кнопка лишь показывает месяц!',
                'empty_cell': '⚠ Это пустая кнопка!'}
        text = data[call.data.replace('it_is_', '')]
        await call.answer(text=text, show_alert=True)

    @staticmethod
    async def _cancel(call: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await call.message.delete()

    async def _show_date(self, call: types.CallbackQuery):
        year, month = list(map(int, call.data.replace('show_date_', '').split('_')))
        await call.message.edit_reply_markup(reply_markup=date_kb(self.get_prefix(), year, month))

    async def _show_calendar(self, msg: types.Message):
        text = '<b>🗓 Выберите дату</b>'
        kb = date_kb(self.get_prefix())
        await msg.answer(text=text, reply_markup=kb, parse_mode='html')

    def _register(self):
        self._router.callback_query.register(self._callback, Text(text_startswith=self.get_prefix()))


class DatetimeManager(DateManager):

    def __init__(self, router: Router, callback: typing.Awaitable, open_on_filter: BaseFilter):
        super().__init__(router, callback, open_on_filter)

    async def choose_date(self, call: types.CallbackQuery, state: FSMContext):
        text = '<b>🕗 Введите время в формате: <code>HH:MM</code></b>'
        await call.message.delete()
        await state.update_data(date=self.get_date(call.data))
        await state.set_state(TimeManagersStates.DatetimeGetter)
        await call.message.answer(text=text, parse_mode='html', reply_markup=cancel_kb())

    @staticmethod
    async def get_datetime(text: str, state: FSMContext) -> datetime:
        try:
            data = await state.get_data()
            _date = data['date']
            hour, minute = list(map(int, text.split(':')))
            return datetime(year=_date.year, month=_date.month, day=_date.day, hour=hour, minute=minute)
        except:
            return None

    def _register(self):
        self._router.callback_query.register(self.choose_date, Text(text_startswith=self.get_prefix()))
        self._router.message.register(self._callback, state=TimeManagersStates.DatetimeGetter)

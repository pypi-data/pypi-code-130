from calendar import monthrange
from datetime import datetime, date
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


cancel_btn = InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel_op')

months = ['Январь', 'Февраль', 'Март', 'Апрель',
          'Май', 'Июнь', 'Июль', 'Август',
          'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


def date_kb(call_data: str, year: int = None, month: int = None) -> InlineKeyboardMarkup:
    null_btn = InlineKeyboardButton(text='\t', callback_data='it_is_empty_cell')

    if year is None or month is None:
        today = date.today()
        year, month = today.year, today.month

    if month > 12:
        year += 1
        month = 1

    elif month < 1:
        year -= 1
        month = 12
    pos, max_day = monthrange(year, month)
    month_str = months[month - 1]

    markup = [
        [
            InlineKeyboardButton(text='<<', callback_data=f'show_date_{year - 1}_{month}'),
            InlineKeyboardButton(text=str(year), callback_data='it_is_year'),
            InlineKeyboardButton(text='>>', callback_data=f'show_date_{year + 1}_{month}')
        ],
        [
            InlineKeyboardButton(text='<<', callback_data=f'show_date_{year}_{month - 1}'),
            InlineKeyboardButton(text=month_str, callback_data='it_is_month'),
            InlineKeyboardButton(text='>>', callback_data=f'show_date_{year}_{month + 1}')
        ],
        [
            InlineKeyboardButton(text=i, callback_data='it_is_weekday') for i in week_days
        ]
    ]

    row = [null_btn for _ in range(pos)]

    for i in range(max_day):
        if len(row) == 7:
            markup.append(row)
            row = []
        row.append(InlineKeyboardButton(text=str(i + 1), callback_data=f'{call_data}{year}_{month}_{i + 1}'))

    for _ in range(7 - len(row)):
        row.append(null_btn)

    markup.append(row)
    markup.append([cancel_btn])
    return InlineKeyboardBuilder(markup).as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardBuilder([[cancel_btn]]).as_markup()

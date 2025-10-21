from operator import call
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Запись финансов', callback_data = 'recording')],
    [InlineKeyboardButton(text='Текущие данные', callback_data = 'current_data')],
    [InlineKeyboardButton(text='Временная статистика', callback_data='time_stat')]
    ])

inline_keyboard_write_finance = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сумма финансов', callback_data = 'all_finance')],
    [InlineKeyboardButton(text='Прибавление', callback_data = 'plus_to_finance'),
    InlineKeyboardButton(text='Траты', callback_data = 'spendings')],
    [InlineKeyboardButton(text='На главную', callback_data='to_main_keyboard')] 
    ])

inline_keyboard_time_stat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='За день', callback_data='time_stat_for_day')],
    [InlineKeyboardButton(text='За неделю', callback_data='time_stat_for_week')],
    [InlineKeyboardButton(text='За год', callback_data='time_stat_for_year')],
    [InlineKeyboardButton(text='На главную', callback_data='to_main_keyboard')]
    ])

exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='На главную', callback_data='to_main_keyboard')]
    ])

months = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}


def getYearsButton(years: list):
    years_button = [
                    [InlineKeyboardButton(text=f"{year}", callback_data=f"year:{year}")] for year in years]
    years_button.append([InlineKeyboardButton(text='На главную', callback_data='to_main_keyboard')])
    return InlineKeyboardMarkup(inline_keyboard=years_button)


def getMonth():
    monthButton = []
    row = []
    for num, name in months.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"month:{num}"))
        if len(row) == 3:
            monthButton.append(row)
            row = []

    if row:
        monthButton.append(row)

    monthButton.append([InlineKeyboardButton(text='На главную', callback_data='to_main_keyboard')])
    return InlineKeyboardMarkup(inline_keyboard=monthButton)




















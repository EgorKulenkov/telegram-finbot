import asyncio
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, user
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.util import to_column_set


import keyboard as kb
from states import *
import request as db

router = Router()

@router.message(Command('start'), StateFilter(None))
async def start_function_keyboard(message: Message):
    await message.answer(text='Выбери опцию:', 
                         reply_markup=kb.start_keyboard)

#======================ОСНОВНЫЕ КНОПКИ============================

@router.callback_query(F.data == 'recording')
async def rec_finance(callback: CallbackQuery):
    await callback.answer('Обработка...')
    await callback.message.edit_text('Запись финансов:', reply_markup=kb.inline_keyboard_write_finance)
    
@router.callback_query(F.data == 'current_data')
async def show_current_data(callback: CallbackQuery):
    await callback.answer('Обработка...')
    all_finance = await db.getAllFinance(user_id=callback.from_user.id) 
    await callback.message.answer(f'Ваши финансы:\n{all_finance}', reply_markup=kb.exit)
    await callback.answer()

@router.callback_query(F.data == 'time_stat')
async def show_time_stat(callback: CallbackQuery):
    await callback.answer('Обработка...')
    await callback.message.edit_text('Временная статистика', reply_markup=kb.inline_keyboard_time_stat)

#======================ДОП КНОПКИ ЗАПИСЬ ФИНАНСОВ===================

@router.callback_query(F.data == 'all_finance')
async def sum_fin(callback: CallbackQuery, state: FSMContext):
    await callback.answer() 
    hasFin = await db.userHasFinance(user_id=callback.from_user.id)
    if hasFin:
        await callback.message.answer('У тебя уже есть запись всех финансов', reply_markup=kb.exit)
    else:
        await state.set_state(SetAllFinance.sum) 
        await callback.message.answer('Введите сумму ваших финансов: ')
        await callback.answer()

@router.callback_query(F.data == 'plus_to_finance')
async def plus_fin(callback: CallbackQuery, state: FSMContext): 
    await state.set_state(SetAllFinance.add_fin_state)
    await callback.message.answer('Введите сумму прибавления: ')
    await callback.answer()

@router.callback_query(F.data == 'spendings')
async def minus_fin(callback: CallbackQuery, state: FSMContext): 
    await state.set_state(SetAllFinance.minus_fin_state)
    await callback.message.answer('Введите сумму трат: ')
    await callback.answer()

#=====================ДОП КНОПКИ ВРЕМ СТАТ==========================

@router.callback_query(F.data=='time_stat_for_day')
async def get_time_stat_for_day(callback: CallbackQuery):
    await callback.answer()
    daySpend = await db.getDayMinFin(user_id=callback.from_user.id)
    await callback.message.answer(f'ТРАТЫ ЗА ДЕНЬ:\n{daySpend}', reply_markup=kb.exit)

@router.callback_query(F.data=='time_stat_for_week')
async def get_time_stat_for_week(callback: CallbackQuery):
    await callback.answer()
    weekSpend = await db.getWeekMinFin(user_id=callback.from_user.id)
    await callback.message.answer(f'ТРАТЫ ЗА НЕДЕЛЮ:\n{weekSpend}', reply_markup=kb.exit)

@router.callback_query(StateFilter(None),F.data=='time_stat_for_year')
async def get_time_stat_for_month(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    years = await db.getYears(callback.from_user.id)
    if not years:
        await callback.message.answer(text='У вас нет ни одной траты')
    else:
        await state.set_state(GetStat.year)
        await callback.message.answer('Выбери год:', reply_markup=kb.getYearsButton(years=years))

@router.callback_query(GetStat.year, F.data.startswith('year:'))
async def year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    year = callback.data.split(":")[1]
    try:
        await state.update_data(year=int(year))
        await state.set_state(GetStat.month)
        await callback.message.answer('Выбери месяц', reply_markup=kb.getMonth())
    except ValueError:
        await callback.message.answer('Я Вас не понял')
    await callback.answer()

@router.callback_query(GetStat.month, F.data.startswith('month:'))
async def year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    month = callback.data.split(":")[1]
    try:
        month = int(month)
        if 1 <= month <= 12:
            await state.update_data(month=month)
            data = await state.get_data()
            expenses = await db.getAll(user_id=callback.from_user.id, data=data)
            await callback.message.answer(text=expenses, reply_markup=kb.start_keyboard)
    except ValueError:
        await callback.message.answer(text='Я вас не понял', reply_markup=kb.exit)
    await callback.answer()

#=====================НА ГЛАВНУЮ=============================
@router.callback_query(F.data == 'to_main_keyboard')
async def go_main_kb(callback: CallbackQuery):
    await callback.answer('Обработка...')
    await callback.message.edit_text('Выберите опцию:', reply_markup=kb.start_keyboard)

#====================STATES==================================
@router.message(SetAllFinance.sum)
async def set_finance(message: Message, state: FSMContext):
    try: 
        amount = float(message.text)
        await state.update_data(sum=amount)
        data = await state.get_data()
        await db.add(user_id=message.from_user.id, data=data) 
    except ValueError:
        await message.answer('Я вас не понял', reply_markup=kb.exit)
    await message.answer(f'Ваши финансы: {amount}') 
    await state.clear()

@router.message(SetAllFinance.add_fin_state)
async def add_to_fin(message: Message, state: FSMContext):
    amount = float(message.text) 
    await db.addToFinance(user_id=message.from_user.id, amount=amount) 
    await state.update_data(add_fin_state=amount)
    await state.set_state(SetAllFinance.description_add)
    await message.answer('Введите описание прибавления: ')

@router.message(SetAllFinance.description_add)
async def description_spend_add_to_fin(message: Message, state: FSMContext):
    descr = str(message.text)
    await state.update_data(description_add=descr)
    data = await state.get_data()
    await db.addObjPlusFin(user_id=message.from_user.id, data=data)
    await message.answer(f"Прибавление: {data['add_fin_state']} BYN\nОписание: {data['description_add']}\nЗаписано!", reply_markup=kb.exit)
    await state.clear()

@router.message(SetAllFinance.minus_fin_state)
async def minus_fin(message: Message, state: FSMContext):
    amount = float(message.text) 
    await db.substractFromFinance(user_id=message.from_user.id, amount=amount)
    await state.update_data(minus_fin_state=amount)
    await state.set_state(SetAllFinance.description_spend)
    await message.answer('Введите описание траты: ')

@router.message(SetAllFinance.description_spend)
async def description_spend_minus_fin(message: Message, state: FSMContext):
    descr = str(message.text)
    await state.update_data(description_spend=descr)
    data = await state.get_data()
    await db.addObjMinFin(user_id=message.from_user.id, data=data)
    await message.answer(f"Трата: {data['minus_fin_state']}\nОписание: {data['description_spend']}\nЗаписано!", reply_markup=kb.exit)
    await state.clear()




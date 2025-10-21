from aiogram.fsm.state import State, StatesGroup


class SetAllFinance(StatesGroup):
    sum = State()
    description_spend = State()
    description_add = State()
    add_fin_state = State()
    minus_fin_state = State()

class GetStat(StatesGroup):
    year = State()
    month = State()



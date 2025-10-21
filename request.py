from datetime import datetime, timedelta, time
from calendar import monthrange

from sqlalchemy.ext.asyncio import async_object_session
from models import async_session
from models import *
from sqlalchemy import select, and_, func, update


#===============================AllFinance Methods===========================
async def add(user_id, data):
    async with async_session() as session:
        session.add(AllFinance(
                user_id = user_id,
                all_finance = data['sum'],
                date = datetime.now())
        )
        await session.commit()

async def userHasFinance(user_id) -> bool:
    async with async_session() as session:
        exist = await session.scalar(select(AllFinance.user_id)
                                      .where(AllFinance.user_id==user_id)
                                      .limit(1))
    return exist is not None

async def substractFromFinance(user_id, amount):
    async with async_session() as session:
        await session.execute(
                update(AllFinance)
                .where(AllFinance.user_id==user_id)
                .values(all_finance=AllFinance.all_finance - amount)
                )
        await session.commit()

async def addToFinance(user_id, amount):
    async with async_session() as session:
        await session.execute(
                update(AllFinance)
                .where(AllFinance.user_id==user_id)
                .values(all_finance=AllFinance.all_finance + amount)
                )
        await session.commit()

async def getYears(user_id):
    async with async_session() as session:
        years = await session.scalars(
                select(func.strftime("%Y",AllFinance.date).label("year"))
                .where(AllFinance.user_id == user_id)
                .distinct()
                .order_by("year")
        )
    return years.all()

async def getAllFinance(user_id):
    async with async_session() as session:
        all_fin = await session.scalar(
                select(AllFinance.all_finance)
                .where(AllFinance.user_id==user_id)
                )
    return all_fin

async def getAll(user_id, data):
    year = data['year']
    month = data['month']
    start_date = datetime(year, month, 1)
    last_date = monthrange(year, month)[1]
    end_date = datetime(year, month, last_date, 23, 59, 59)
    async with async_session() as session:
        expenses = session.scalars(select(AllFinance).where(
            and_(AllFinance.user_id == user_id,
                 AllFinance.date >= start_date,
                 AllFinance.date <= end_date)))
        return answerExpenses(expenses.all())


def answerExpenses(expenses):
    if not expenses:
        return "В этом месяце трат НЕ БЫЛО"

    sum = 0
    answer = []

    for exp in expenses:
        date = exp.date.strftime("%d.%m.%Y")
        answer.append(f"{date}\n{exp.sum}\n{exp.description}")
        sum += exp.sum

    answer.append("-------------")
    return "\n\n".join(answer)

#===================================PlusFin Methods=================================
async def addObjPlusFin(user_id, data):
    async with async_session() as session:
        session.add(PlusFin(
                    user_id = user_id,
                    plus_fin = data['add_fin_state'],
                    description_plus = data['description_add'],
                    date = datetime.now())
                    )
        await session.commit()

#===================================MinFin Methods=================================

days_dict = {
    0: 'Понедельник: ',
    1: 'Вторник: ',
    2: 'Среда: ',
    3: 'Четверг: ',
    4: 'Пятница: ',
    5: 'Суббота: ',
    6: 'Воскресенье: '
}


async def addObjMinFin(user_id, data):
    async with async_session() as session:
        session.add(MinusFin(
                    user_id = user_id,
                    minus_fin = data['minus_fin_state'],
                    description_minus = data['description_spend'],
                    date = datetime.now())
                    )
        await session.commit()

async def getDayMinFin(user_id):
    day = datetime.today()
    start_date = datetime.combine(day, datetime.min.time())
    end_date = datetime.combine(day, datetime.max.time())
    async with async_session() as session:
        expenses = await session.scalars(select(MinusFin)
                                         .where(MinusFin.user_id == user_id,
                                                MinusFin.date >= start_date,
                                                MinusFin.date <= end_date)
                                         )
    result = []
    for exp in expenses.all():
        result.append(f"Трата: {exp.minus_fin} BYN\nОписание: {exp.description_minus}")

    return "\n------------------------\n".join(result) if result else "Трат за день нет!"


async def getWeekMinFin(user_id):
    week = datetime.today()
    start_week = datetime.combine(week - timedelta(week.weekday()), time.min)
    end_week = datetime.combine(week + timedelta(6 - week.weekday()), time.max)
    
    async with async_session() as session:
        expenses = await session.scalars(select(MinusFin)
                                         .where(MinusFin.user_id == user_id,
                                                MinusFin.date >= start_week,
                                                MinusFin.date <= end_week)
                                         )
    result = []
    week_sums = {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6: 0.0
    }
        
    for exp in expenses.all():
        day = exp.date.weekday()
        week_sums[day] += exp.minus_fin
    
    for day in range(7):
        result.append(f'{days_dict[day]}: {week_sums[day]:.2f} BYN')
    
    all_sum = sum(week_sums.values())
    if all_sum == 0: return 'Трат за неделю не было!'
    avg_week = all_sum/7
    result.append(f'\nИтого: {all_sum:.2f}\nСреднее: {avg_week:.2f}')
    return "\n".join(result) if result else 'Трат за неделю не было!'



                          










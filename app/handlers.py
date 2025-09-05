from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from app.database.models import getDay, check_user_exists, update_user_group, add_user

import app.keyboard as kb

class Reg(StatesGroup):
    group = State()

router = Router()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await state.clear()
    if await check_user_exists(message.from_user.id):
        await message.answer(f'С возвращением...',reply_markup=kb.main)
    else:
        await state.set_state(Reg.group)
        await message.answer("Введите номер группы(только число)")
    
@router.message(F.text == 'ping') #ping
async def qwerty(message: Message):
    await print(datetime.now().hour)  # текущее время
    await print(datetime.today().date().strftime('%d.%m.%Y'))  # дата сегодня
    await print((datetime.today() + timedelta(days=1)).date().strftime('%d.%m.%Y'))  # дата завтра

    today = datetime.today()
    today_str = today.date().strftime('%d.%m.%Y')
    tomorrow_str = (today + timedelta(days=1)).date().strftime('%d.%m.%Y')
    if datetime.now().hour < 17:
        date_to_use = today_str
    else:
        date_to_use = tomorrow_str

    await message.answer('pong')

@router.message(F.text == 'Звонки')
async def qwerty(message: Message):
    schedule_text = """(Будни)\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:55 - 12:40\n3. 13:00 - 13:45 | 13:55 - 14:40\n4. 14:50 - 15:35 | 15:45 - 16:30\n5. 16:40 - 17:25 | 17:35 - 18:20\n\n(Суббота)\n1. 09:00 - 09:45 | 09:55 - 10:40\n2. 10:50 - 11:35 | 11:55 - 12:40\n3. 12:50 - 13:35 | 13:45 - 14:30\n4. 14:40 - 15:25 | 15:35 - 16:20\n5. 16:30 - 17:15 | 17:25 - 18:10"""
    
    await message.answer(schedule_text)

@router.message(F.text == 'Неделя')
async def week(message: Message):
    today = datetime.today().date()
    weekday_num = today.weekday()
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    msg_text = ""
    
    if weekday_num == 6:
        start_date = today + timedelta(days=1)
        days_count = 5
    else:
        start_date = today
        days_count = 5 - weekday_num 
    
    if weekday_num <= 5:
        days_count += 1
    
    for i in range(days_count):
        current_date = start_date + timedelta(days=i)
        formatted_date = current_date.strftime('%d.%m.%Y')
        
        day_schedule = await getDay(message.from_user.id, formatted_date)
        
        current_weekday_num = current_date.weekday()
        weekday_name = weekdays[current_weekday_num]
        is_today = " (сегодня)" if current_date == today else ""
        msg_text += f"___{weekday_name}{is_today}, {formatted_date}___\n"
        
        if day_schedule:
            prev_value = None
            for record in day_schedule:
                if record[3] == 6 and prev_value != 5:
                    prev_value = record[3]
                    continue
                msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
                prev_value = record[3]
        else:
            msg_text += "Пар нет\n"
        
        msg_text += "\n"
    
    if msg_text.strip():
        await message.answer(msg_text, reply_markup=kb.week_next)
    else:
        await message.answer("На неделю нет пар")

@router.callback_query(F.data == 'next_week')
async def next_week(callback: CallbackQuery):
    today = datetime.today().date()
    weekday_num = today.weekday()
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    msg_text = ""
    
    if weekday_num == 6:
        next_monday = today + timedelta(days=1)
    else:
        next_monday = today + timedelta(days=7 - weekday_num)
    
    for i in range(6):
        current_date = next_monday + timedelta(days=i)
        formatted_date = current_date.strftime('%d.%m.%Y')
        
        day_schedule = await getDay(callback.from_user.id, formatted_date)
        
        current_weekday_num = current_date.weekday()
        weekday_name = weekdays[current_weekday_num]
        msg_text += f"___{weekday_name}, {formatted_date}___\n"
        
        if day_schedule:
            prev_value = None
            for record in day_schedule:
                if record[3] == 6 and prev_value != 5:
                    prev_value = record[3]
                    continue
                msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
                prev_value = record[3]
        else:
            msg_text += "Пар нет\n"
        
        msg_text += "\n"
    
    if msg_text.strip():
        await callback.message.edit_text(msg_text, reply_markup=kb.week_current)
    else:
        await callback.message.edit_text("На следующую неделю нет пар", reply_markup=kb.week_current)

@router.callback_query(F.data == 'current_week')
async def week(callback: CallbackQuery):
    today = datetime.today().date()
    weekday_num = today.weekday()
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    msg_text = ""
    
    if weekday_num == 6:
        start_date = today + timedelta(days=1)
        days_count = 5
    else:
        start_date = today
        days_count = 5 - weekday_num 
    
    if weekday_num <= 5:
        days_count += 1
    
    for i in range(days_count):
        current_date = start_date + timedelta(days=i)
        formatted_date = current_date.strftime('%d.%m.%Y')
        
        day_schedule = await getDay(callback.from_user.id, formatted_date)
        
        current_weekday_num = current_date.weekday()
        weekday_name = weekdays[current_weekday_num]
        is_today = " (сегодня)" if current_date == today else ""
        msg_text += f"___{weekday_name}{is_today}, {formatted_date}___\n"
        
        if day_schedule:
            prev_value = None
            for record in day_schedule:
                if record[3] == 6 and prev_value != 5:
                    prev_value = record[3]
                    continue
                msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
                prev_value = record[3]
        else:
            msg_text += "Пар нет\n"
        
        msg_text += "\n"
    
    if msg_text.strip():
        await callback.message.edit_text(msg_text, reply_markup=kb.week_next)
    else:
        await callback.message.edit_text("На неделю нет пар")

@router.message(F.text == 'День')
async def day(message: Message):
    today = datetime.today().date().strftime('%d.%m.%Y')
    tomorrow = (datetime.today() + timedelta(days=1)).date().strftime('%d.%m.%Y')
    day = await getDay(message.from_user.id, today)
    db_date = datetime.strptime(day[0][1], '%d.%m.%Y').date()
    weekday_num = db_date.weekday()
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    weekday_name = weekdays[weekday_num]
    msg_text = f"___{weekday_name} (сегодня), {today}___\n"
    if day:
        prev_value = None
        for record in day:
            if record[3] == 6 and prev_value != 5:
                prev_value = record[3]
                continue
            msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
            prev_value = record[3]
    else:
        msg_text += "Пар нет"
    msg_text += "\n"
    next_day = await getDay(message.from_user.id, tomorrow)
    db_date = datetime.strptime(next_day[0][1], '%d.%m.%Y').date()
    weekday_name = weekdays[weekday_num+1]
    msg_text += f"___{weekday_name} (завтра), {tomorrow}___\n"
    if next_day:
        prev_value = None
        for record in next_day:
            if record[3] == 6 and prev_value != 5:
                prev_value = record[3]
                continue
            msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
            prev_value = record[3]
    else:
        msg_text += "Пар нет"
    if msg_text:
        await message.answer(msg_text)
    else:
        await message.answer("На сегодня/завтра нет пар")

@router.message(F.photo)
async def photo(message: Message):
    await message.answer('...')

@router.message(Command('reg'))
async def reg(message: Message, state: FSMContext):
    await state.set_state(Reg.group)
    await message.answer("Введите номер группы(только число)", reply_markup=None)

@router.message(Reg.group)
async def reg_answer(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    data = await state.get_data()
    try:
        group_number = int(data["group"])
    except ValueError:
        await message.answer('Номер группы должен быть числом!!!')
        return
    if await check_user_exists(message.from_user.id):
        res = await update_user_group(message.from_user.id, group_number)
        await message.answer(f'Заменил, впредь не ошибайся',reply_markup=kb.main)
    else:
        await add_user(message.from_user.id,group_number,0,0)
        await message.answer(f'Теперь ты пользователь\n Стабильность, корректность, да и в общем работоспобность НЕ ГАРАНТИРОВАНА!!!',reply_markup=kb.main)
    await state.clear()


@router.callback_query(F.data == 'day')
async def day(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Hello', reply_markup=await kb.inline_days())
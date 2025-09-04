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
    await message.answer('pong')

@router.message(F.text == 'День')
async def day(message: Message):
    day = await getDay(message.from_user.id)
    if day:
        db_date = datetime.strptime(day[0][1], '%d.%m.%Y').date()
    
        if datetime.today().date() == db_date:
            state = "сегодня"
        else:
            state = "завтра"
    
        weekday_num = db_date.weekday()
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        weekday_name = weekdays[weekday_num]
        msg_text = f"___{weekday_name} ({state}), {day[0][1]}___\n"
        for record in day:
            msg_text += f"{record[3]}. {record[4]} ({record[5]})\n"
    
        await message.answer(msg_text)
    else:
        await message.answer("Нет данных на этот день")

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
        await message.answer(f'Теперь ты пользователь/n Стабильность, корректность, да и в общем работоспобность НЕ ГАРАНТИРОВАНА!!!',reply_markup=kb.main)
    await state.clear()


@router.callback_query(F.data == 'day')
async def day(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('Hello', reply_markup=await kb.inline_days())
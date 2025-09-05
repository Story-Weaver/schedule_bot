from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='День'), KeyboardButton(text='Неделя')],
    [KeyboardButton(text='Звонки')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

week_next = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Дальше', callback_data='next_week')]
])

week_current = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='current_week')]
])

days = ['','']

async def inline_days():
    keyboard = InlineKeyboardBuilder()
    for day in days:
        keyboard.add(InlineKeyboardButton(text=day, url = 'https://github.com'))
    return keyboard.adjust(2).as_markup()
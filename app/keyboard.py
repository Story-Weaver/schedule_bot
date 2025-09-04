from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='День'), KeyboardButton(text='Неделя')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

main2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='День', callback_data='day'), InlineKeyboardButton(text='Неделя', callback_data='week')]
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='github', url='https://github.com')]
])
days = ['mon','tue','wed']

async def inline_days():
    keyboard = InlineKeyboardBuilder()
    for day in days:
        keyboard.add(InlineKeyboardButton(text=day, url = 'https://github.com'))
    return keyboard.adjust(2).as_markup()
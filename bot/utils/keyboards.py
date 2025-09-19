from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.models import Products, Category
from bot.utils.messages import Messages


class ReplyKeyboard:
    @staticmethod
    def catalog_keyboard(categories: list[Category]):
        keyboard = []
        for el in categories:
            button = [KeyboardButton(text=el.name)]
            keyboard.append(button)
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    @staticmethod
    def menu_admin_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=Messages.ADD_PRODUCT_ADMIN)],
            [KeyboardButton(text=Messages.REDACTOR_PRODUCT_ADMIN)],
            [KeyboardButton(text=Messages.SHOW_ORDER_ADMIN)],
            [KeyboardButton(text=Messages.EXIT)]
        ], resize_keyboard=True)
    
    @staticmethod
    def exit_keyboard():
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=Messages.EXIT)]
        ], resize_keyboard=True)


class InlineKeyboards:
    @staticmethod
    def first_keyboard():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=Messages.FIRST_INLINE, callback_data="pass")]
        ])
        
    @staticmethod
    def catalog_keyboard(categories: list[Category]):
        keyboard = []
        for el in categories:
            button = [InlineKeyboardButton(text=el.name, callback_data=f'category_{el.id}')]
            keyboard.append(button)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
        
    

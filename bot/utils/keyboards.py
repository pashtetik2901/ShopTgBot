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
    def build_edit_keyboard(product_id: int) -> InlineKeyboardMarkup:
        keyboard_buttons = [
            [
                InlineKeyboardButton(text="Изменить название", callback_data=f"rdc_name_{product_id}"),
                InlineKeyboardButton(text="Изменить описание", callback_data=f"rdc_description_{product_id}")
            ],
            [
                InlineKeyboardButton(text="Изменить цену", callback_data=f"rdc_price_{product_id}"),
                InlineKeyboardButton(text="Изменить фото URL", callback_data=f"rdc_photo_url_{product_id}")
            ],
            [
                InlineKeyboardButton(text="Сохранить изменения", callback_data=f"rdc_save_{product_id}"),
                InlineKeyboardButton(text="Отменить редактирование", callback_data=f"rdc_cancel_{product_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    
    
    @staticmethod
    def choose_element_rdc(product_id: int):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Изменить название", callback_data=f'rdc_name_{product_id}')],
            [InlineKeyboardButton(text="Изменить описание", callback_data=f'rdc_description_{product_id}')],
            [InlineKeyboardButton(text="Изменить стоимость", callback_data=f'rdc_price_{product_id}')],
            [InlineKeyboardButton(text="Изменить фото", callback_data=f'rdc_photo_{product_id}')],
        ])
    
    @staticmethod
    def all_product(product_list: list[Products]):
        keyboard = []
        for product in product_list:
            button = [InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}")]
            keyboard.append(button)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
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
    
        
    

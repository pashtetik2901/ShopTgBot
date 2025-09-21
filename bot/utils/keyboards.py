from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.models import Products, Category, Order
from bot.utils.messages import Messages


class ReplyKeyboard:
    @staticmethod
    def get_main_menu_keyboard():
        """Основное меню с Reply клавиатурой"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🛍️ Каталог"),
                    KeyboardButton(text="🛒 Корзина")
                ],
                [
                    KeyboardButton(text="📋 Мои заказы"),
                    KeyboardButton(text="ℹ️ Помощь")
                ]
            ],
            resize_keyboard=True
        )  
    
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
    def admin_all_product(product_list):
        """Клавиатура со списком товаров для админа"""
        inline_keyboard = []
        
        for product in product_list:
            inline_keyboard.append([
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=f"admin_product_{product.id}"  # Админский префикс!
                )
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    @staticmethod
    def user_all_product(product_list, category_id=None):
        """Клавиатура со списком товаров для пользователя"""
        inline_keyboard = []
        
        for product in product_list:
            inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"{product.name} - {product.price} руб.",
                    callback_data=f"product_{product.id}"  # Обычный префикс
                )
            ])
        
        # Кнопка возврата
        back_button = InlineKeyboardButton(
            text="⬅️ Назад к категориям",
            callback_data="back_to_categories"
        )
        inline_keyboard.append([back_button])
        
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    @staticmethod
    def admin_product_detail_keyboard(product_id):
        """Клавиатура для детальной страницы товара (админ)"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Название", callback_data=f"rdc_name_{product_id}"),
                InlineKeyboardButton(text="📝 Описание", callback_data=f"rdc_description_{product_id}")
            ],
            [
                InlineKeyboardButton(text="💰 Цена", callback_data=f"rdc_price_{product_id}"),
                InlineKeyboardButton(text="🖼️ Фото", callback_data=f"rdc_photo_url_{product_id}")
            ],
            [
                InlineKeyboardButton(text="✅ Сохранить", callback_data=f"rdc_save_{product_id}"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"rdc_cancel_{product_id}")
            ]
        ])

    @staticmethod
    def user_product_detail_keyboard(product_id):
        """Клавиатура для детальной страницы товара (пользователь)"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Добавить в корзину",
                    callback_data=f"add_to_cart_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к товарам",
                    callback_data="back_to_products"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏪 В каталог",
                    callback_data="back_to_categories"
                )
            ]
        ])

    @staticmethod
    def get_quantity_keyboard(product_id):
        """Клавиатура для выбора количества товара"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1", callback_data=f"quantity_{product_id}_1"),
                InlineKeyboardButton(text="2", callback_data=f"quantity_{product_id}_2"),
                InlineKeyboardButton(text="3", callback_data=f"quantity_{product_id}_3")
            ],
            [
                InlineKeyboardButton(text="5", callback_data=f"quantity_{product_id}_5"),
                InlineKeyboardButton(text="10", callback_data=f"quantity_{product_id}_10")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_quantity")
            ]
        ])

    @staticmethod
    def get_cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:
        """Клавиатура для корзины с товарами"""
        keyboard = InlineKeyboardBuilder()
        
        for item in cart_items:
            # Используем правильный ключ для ID элемента корзины
            item_id = item['id']  # Изменено с item['item_id'] на item['id']
            product_name = item['product'].name
            
            keyboard.row(
                InlineKeyboardButton(
                    text=f"❌ Удалить {product_name}",
                    callback_data=f"remove_from_cart_{item_id}"
                )
            )
        
        keyboard.row(
            InlineKeyboardButton(
                text="🗑️ Очистить корзину",
                callback_data="clear_cart"
            )
        )
        
        keyboard.row(
            InlineKeyboardButton(
                text="✅ Оформить заказ",
                callback_data="create_order"
            )
        )
        
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад в каталог",
                callback_data="back_to_catalog"
            )
        )
        
        return keyboard.as_markup()

    @staticmethod
    def get_cart_empty_keyboard():
        """Клавиатура для пустой корзины"""
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🛍️ В каталог", callback_data="back_to_catalog")
        ]])

    @staticmethod
    def get_confirm_clear_keyboard():
        """Клавиатура подтверждения очистки корзины"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="confirm_clear_cart"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel_clear_cart")
            ]
        ])
    
    @staticmethod
    def get_categories_keyboard(categories):
        """Клавиатура с категориями товаров"""
        buttons = []
        for category in categories:
            buttons.append(InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            ))
        
        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        # Добавляем кнопки по 2 в ряд
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.inline_keyboard.append([buttons[i], buttons[i + 1]])
            else:
                keyboard.inline_keyboard.append([buttons[i]])
        
        return keyboard

    @staticmethod
    def get_products_keyboard(products, category_id=None):
        """Клавиатура с товарами категории"""
        buttons = []
        for product in products:
            buttons.append(InlineKeyboardButton(
                text=f"{product.name} - {product.price} руб.",
                callback_data=f"product_{product.id}"
            ))
        
        # Кнопка возврата
        back_button = InlineKeyboardButton(
            text="⬅️ Назад к категориям",
            callback_data="back_to_categories"
        )
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        # Добавляем кнопки товаров
        for button in buttons:
            keyboard.inline_keyboard.append([button])
        
        # Добавляем кнопку возврата
        keyboard.inline_keyboard.append([back_button])
        
        return keyboard

    @staticmethod
    def get_product_detail_keyboard(product_id, category_id=None):
        """Клавиатура для детальной страницы товара"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        # Кнопка добавления в корзину
        keyboard.inline_keyboard.append([InlineKeyboardButton(
            text="🛒 Добавить в корзину",
            callback_data=f"add_to_cart_{product_id}"
        )])
        
        # Кнопка возврата к товарам категории
        if category_id:
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text="⬅️ К товарам категории",
                callback_data=f"category_{category_id}"
            )])
        else:
            keyboard.inline_keyboard.append([InlineKeyboardButton(
                text="⬅️ Назад к товарам",
                callback_data="back_to_products"
            )])
        
        keyboard.inline_keyboard.append([InlineKeyboardButton(
            text="🏪 В каталог",
            callback_data="back_to_categories"
        )])
        
        return keyboard

    @staticmethod
    def get_empty_category_keyboard():
        """Клавиатура для пустой категории"""
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="⬅️ Назад к категориям",
                callback_data="back_to_categories"
            )
        ]])

    @staticmethod
    def all_order(order_list: list[Order]):
        keyboard = []
        for order in order_list:
            button = [InlineKeyboardButton(
                text=order.id, callback_data=f"order_{order.id}")]
            keyboard.append(button)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def build_edit_keyboard(product_id: int) -> InlineKeyboardMarkup:
        keyboard_buttons = [
            [
                InlineKeyboardButton(
                    text="Изменить название", callback_data=f"rdc_name_{product_id}"),
                InlineKeyboardButton(
                    text="Изменить описание", callback_data=f"rdc_description_{product_id}")
            ],
            [
                InlineKeyboardButton(text="Изменить цену",
                                     callback_data=f"rdc_price_{product_id}"),
                InlineKeyboardButton(
                    text="Изменить фото URL", callback_data=f"rdc_photo_url_{product_id}")
            ],
            [
                InlineKeyboardButton(
                    text="Сохранить изменения", callback_data=f"rdc_save_{product_id}"),
                InlineKeyboardButton(
                    text="Отменить редактирование", callback_data=f"rdc_cancel_{product_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    @staticmethod
    def choose_element_rdc(product_id: int):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Изменить название",
                                  callback_data=f'rdc_name_{product_id}')],
            [InlineKeyboardButton(text="Изменить описание",
                                  callback_data=f'rdc_description_{product_id}')],
            [InlineKeyboardButton(text="Изменить стоимость",
                                  callback_data=f'rdc_price_{product_id}')],
            [InlineKeyboardButton(text="Изменить фото",
                                  callback_data=f'rdc_photo_{product_id}')],
        ])

    @staticmethod
    def all_product(product_list: list[Products]):
        keyboard = []
        for product in product_list:
            button = [InlineKeyboardButton(
                text=product.name, callback_data=f"product_{product.id}")]
            keyboard.append(button)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def first_keyboard():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=Messages.FIRST_INLINE, callback_data="pass")]
        ])

    @staticmethod
    def catalog_keyboard(categories: list[Category]):
        keyboard = []
        for el in categories:
            button = [InlineKeyboardButton(
                text=el.name, callback_data=f'category_{el.id}')]
            keyboard.append(button)
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
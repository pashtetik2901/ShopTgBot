# Состояния для FSM
from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    waiting_payment = State()


class DialogState(StatesGroup):
    waiting_for_message: State = State()
    waiting_for_reply = State()
    
class StatusState(StatesGroup):
    user = State()
    admin = State()
    
class AddProductState(StatesGroup):
    wait_category = State()
    wait_name = State()
    wait_description = State()
    wait_price = State()
    wait_photo = State()
    
class RedactroState(StatesGroup):
    choosing_field = State()
    waiting_for_value = State()
    
class CartStates(StatesGroup):
    waiting_quantity = State()
    confirm_clear = State()
    
class OrderStates(StatesGroup):
    enter_name = State()        # Ввод имени
    enter_phone = State()       # Ввод телефона
    choose_delivery = State()   # Выбор способа доставки
    enter_address = State()     # Ввод адреса (если нужно)
    confirm_order = State()    
    
from aiogram.fsm.state import State, StatesGroup

class AdminOrderStates(StatesGroup):
    # Основные состояния управления заказами
    choose_status = State()          # Выбор статуса для изменения
    view_orders = State()            # Просмотр списка заказов
    view_order_details = State()     # Просмотр деталей заказа
    
    # Дополнительные состояния для расширения функционала
    search_orders = State()          # Поиск заказов
    enter_search_query = State()     # Ввод поискового запроса
    
    filter_orders = State()          # Фильтрация заказов
    choose_filter_type = State()     # Выбор типа фильтра
    enter_filter_value = State()     # Ввод значения фильтра
    
    edit_order = State()             # Редактирование заказа
    edit_order_field = State()       # Редактирование конкретного поля
    enter_new_value = State()        # Ввод нового значения
    
    notify_customer = State()        # Уведомление клиента
    enter_notification_text = State()  # Ввод текста уведомления
    
    export_orders = State()          # Экспорт заказов
    choose_export_format = State()   # Выбор формата экспорта
    
    create_order = State()           # Создание заказа вручную
    enter_customer_info = State()    # Ввод информации о клиенте
    enter_order_items = State()      # Ввод товаров заказа
    
    cancel_order = State()           # Отмена заказа
    confirm_cancellation = State()   # Подтверждение отмены
    enter_cancellation_reason = State()  # Причина отмены
    
    # Статистика и аналитика
    view_statistics = State()        # Просмотр статистики
    choose_stat_period = State()     # Выбор периода статистики
    
    # Управление возвратами
    process_refund = State()         # Обработка возврата
    enter_refund_amount = State()    # Ввод суммы возврата
    confirm_refund = State()         # Подтверждение возврата
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
    
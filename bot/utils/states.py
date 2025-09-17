# Состояния для FSM
from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    waiting_payment = State()


class DialogState(StatesGroup):
    waiting_for_message: State = State()
    waiting_for_reply = State()
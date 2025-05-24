from aiogram.fsm.state import StatesGroup, State

class DishNavigation(StatesGroup):
    waiting_for_quantity = State()

user_lang = {}
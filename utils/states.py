from aiogram.fsm.state import State, StatesGroup


class ChoosingEvent(StatesGroup):
    """Выбор мероприятия при /start"""
    waiting_for_event = State()


class AcceleratorStates(StatesGroup):
    """Регистрация в Акселератор"""
    waiting_for_name = State()
    waiting_for_project_name = State()
    waiting_for_email = State()
    waiting_for_tg = State()
    waiting_for_track = State()
    waiting_for_stage = State()
    waiting_for_description = State()
    waiting_for_pizzapitch = State()
    waiting_for_presentation_url = State()
    waiting_for_team = State()
    waiting_for_hse = State()
    waiting_for_consent = State()
    waiting_for_confirmation = State()


class EventStates(StatesGroup):
    """Регистрация на Мероприятия"""
    waiting_for_name = State()
    waiting_for_hse = State()
    waiting_for_edu_program = State()
    waiting_for_tg = State()
    waiting_for_question = State()
    waiting_for_consent = State()
    waiting_for_confirmation = State()


class AdminStates(StatesGroup):
    waiting_for_audience = State()   # Выбор аудитории рассылки
    waiting_for_broadcast = State()  # Текст рассылки

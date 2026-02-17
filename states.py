from aiogram.fsm.state import StatesGroup, State

class MainStates(StatesGroup):
    AI_CHAT = State()
    TEST = State()
    MANAGER_TEXT = State()
    MANAGER_CONTACT = State()
    ADMIN_WAIT_OPENAI_KEY = State()
    ADMIN_WAIT_ASSISTANT_ID = State()
    ADMIN_WAIT_VECTOR_STORE_ID = State()

from aiogram.dispatcher.filters.state import StatesGroup, State


class TasksStatesGroup(StatesGroup):
    set_task_description = State()

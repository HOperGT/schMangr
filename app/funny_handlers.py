import asyncio
import random
import sqlite3
import app.keyboards as kb

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN 
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router_funny = Router()


class UserStates(StatesGroup):
    DefaultState = State()  # Состояние по умолчанию (пользователь ничего не делает)
    ActiveState = State()  # Например, пользователь в процессе заполнения формы



#Ответы на случайные сообщения только в состоянии DefaultState
@router_funny.message(UserStates.DefaultState)
async def random_funny_response(message: types.Message):

    commands_by_group = {
        "Основные команды": ["/start", "/help", "/add_class"],
        "Настройки": ["/settings", "/language"],
        "Дополнительные функции": ["/info", "/stats"]
        }
    mmessage = f"Список доступных команд:\n"
    for group_name, commandss in commands_by_group.items():
            mmessage += f"\n**{group_name}:**\n"
            for commandd in commandss:
                mmessage += f"  • {commandd}\n"
    await message.answer(mmessage) 
    
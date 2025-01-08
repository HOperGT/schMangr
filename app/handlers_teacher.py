import asyncio
import sqlite3
import time
import app.keyboards as kb
import json
import requests

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
from aiogram.enums.parse_mode import ParseMode

router_tech = Router()


@router_tech.message(Command("add_class"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1:  
        await message.reply(f"Добавление класса и/или добавление расписания.\nПерейдите на оффициальное веб-приложение бота.", reply_markup= kb.class_menu())
        text_to_copy = f'Введите номер при входе`\n {user_id}`'
        await message.answer(text_to_copy, parse_mode=ParseMode.MARKDOWN_V2)
        
    else:
        await message.reply(f"Только учителя могут управлять классами!")    

         






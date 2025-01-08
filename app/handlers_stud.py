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



router_stud = Router()


@router_stud.message(Command("view_class"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.reply(f"Просмотр расписания класса..\nПерейдите на оффициальное веб-приложение бота.", reply_markup= kb.class_menu())
    text_to_copy = f'Введите номер при входе`\n {user_id}`'
    await message.answer(text_to_copy, parse_mode=ParseMode.MARKDOWN_V2)
    
         
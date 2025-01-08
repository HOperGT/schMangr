import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F, Router
from aiogram.types.callback_query import CallbackQuery
from config import OWNER_TELEGRAM_ID
from app.funny_handlers import  UserStates
from config import TOKEN 
from aiogram import Bot, Router, types
from aiogram.filters import Command

import sqlite3

bot = Bot(token=TOKEN)
routerHP = Router()

# Подключение к базе SQLite
conn = sqlite3.connect('users.db')
cursor = conn.cursor()


@routerHP.message(Command('admin_message'))
async def admin_message_handler(message: types.Message):
    """
    Обработка команды /admin_message. Отправляет указанное сообщение всем пользователям.
    """
    # Проверка, является ли пользователь администратором
    if message.from_user.id != 1441658354:  # Замените на ваш ID администратора
        await message.reply("У вас нет прав для отправки сообщений!")
        return

    # Получаем текст сообщения после команды
    message_text = message.text.replace('/admin_message', '').strip()

    if not message_text:
        await message.reply("Пожалуйста, укажите текст сообщения после команды.")
        return

    # Получение всех user_id из базы данных
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    if not users:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    sent_count = 0
    failed_count = 0

    # Отправка сообщения всем пользователям
    for user in users:
        user_id = str(user[0])
        try:
            await bot.send_message(chat_id=user_id, text=message_text)  # Изменения тут
            sent_count += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed_count += 1

    # Подтверждение отправки
    await message.reply(f"Сообщение было отправлено {sent_count} пользователям, не удалось отправить {failed_count}.")


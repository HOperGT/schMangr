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
bot = Bot(token=TOKEN)
router_tech = Router()
class SendMesEvent(StatesGroup):
    waiting_for_mess = State()
    all_waiting_for_mess = State()


@router_tech.message(Command("add_class"))
async def add_command(message: types.Message, state: FSMContext):
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
        await message.answer(f"Нажмите на номер для копирования.")
    else:
        await message.reply(f"Только учителя могут управлять классами!")    

         

@router_tech.message(Command("send_Events"))
async def view_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1: 
        await message.reply(f"Выберите, что вы хотите сделать.", reply_markup= kb.choose_view()) 

@router_tech.callback_query(lambda f: f.data == "all_send")
async def all_send(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,))
    username = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1:
        await state.set_state(SendMesEvent.all_waiting_for_mess)
        await callback.message.answer(f"Напишите текст для отправки, для отмены введите /notSend")
    else:
        await callback.message.answer("У вас нет прав для отправки сообщений!") 


@router_tech.message(SendMesEvent.all_waiting_for_mess)
async def check_all_mess(message: types.Message, state: FSMContext):
    message_txt = message.text
    
    if not message_txt:
        await message.reply("Пожалуйста, укажите текст сообщения.")
        return
       
    if message_txt == '/notSend':
        await message.answer(f"Отмена операции отправки сообщения!")
        await state.clear()
        return

    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
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
            # await bot.send_message(chat_id=user_id, text=message_dataee)
            await bot.send_message(chat_id=user_id, text=message_txt)  # Изменения тут
            sent_count += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed_count += 1

    # Подтверждение отправки
    await message.reply(f"Сообщение было отправлено {sent_count} пользователям, не удалось отправить {failed_count}.")
    await state.clear()

@router_tech.callback_query(lambda f: f.data == "send_choose")
async def choose_send(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1:
        await callback.message.answer(f"Выберите класс: ", reply_markup=kb.generate_sendmessclass())
    else:
        await callback.message.reply("У вас нет прав для отправки сообщений!") 




@router_tech.callback_query(lambda f: f.data.startswith('view_'))
async def send_cshoose_mess(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Извлекаем class_id из callback.data
    class_id = callback.data.split('view_')[1]

    # Устанавливаем class_id в состояние
    await state.update_data(class_id=class_id)

    # Устанавливаем состояние ожидания сообщения
    await state.set_state(SendMesEvent.waiting_for_mess)

    await callback.message.answer(f"Напишите текст для отправки, для отмены введите /notSend")

@router_tech.message(SendMesEvent.waiting_for_mess)
async def check_mess(message: types.Message, state: FSMContext):
    # Получаем данные состояния, ожидая ответ асинхронной функции
    data = await state.get_data()
    class_id = data.get('class_id')  # Извлекаем class_id из данных состояния

    message_txt = message.text

    if not message_txt:
        await message.reply("Пожалуйста, укажите текст сообщения.")
        return

    if message_txt == '/notSend':
        await message.answer("Отмена операции отправки сообщения!")
        await state.clear()
        return

    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()

    # Обратите внимание, что class_id теперь корректно передан
    cursor.execute("SELECT user_id FROM users WHERE class_id = ?", (class_id,))
    class_users = cursor.fetchall()  # Получаем всех пользователей с классом class_id

    conn.close()

    if not class_users:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    sent_count = 0
    failed_count = 0

    # Отправка сообщения всем пользователям
    for user in class_users:
        user_id = str(user[0])
        try:
            await bot.send_message(chat_id=user_id, text=message_txt)
            sent_count += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed_count += 1

    # Подтверждение отправки
    await message.reply(f"Сообщение было отправлено {sent_count} пользователям, не удалось отправить {failed_count}.")
    await state.clear()








    # # Получаем текст сообщения после команды
    # message_text = message.text.replace('/admin_message', '').strip()

    # if not message_text:
    #     await message.reply("Пожалуйста, укажите текст сообщения после команды.")
    #     return

    # # Получение всех user_id из базы данных
    # cursor.execute("SELECT user_id FROM users")
    # users = cursor.fetchall()

    # if not users:
    #     await message.reply("Нет зарегистрированных пользователей.")
    #     return

    # sent_count = 0
    # failed_count = 0

    # # Отправка сообщения всем пользователям
    # for user in users:
    #     user_id = str(user[0])
    #     try:
    #         await bot.send_message(chat_id=user_id, text=message_text)  # Изменения тут
    #         sent_count += 1
    #     except Exception as e:
    #         print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    #         failed_count += 1

    # # Подтверждение отправки
    # await message.reply(f"Сообщение было отправлено {sent_count} пользователям, не удалось отправить {failed_count}.")

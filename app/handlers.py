import asyncio
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
from app.funny_handlers import  UserStates
from app.postGet import export_db_to_json, send_data_to_website

class TeacherLogin(StatesGroup):
    waiting_for_login = State()

    
router = Router()

def generate_commands_message():
    commands_by_group = {
        "Основные команды": ["/start", "/help", "/add_class"],
        "Настройки": ["/admin_message", "/language"],
        "Дополнительные функции": ["/info", "/stats"]
    }

    # Начальная строка списка команд
    mmessage = "Список доступных команд:\n"

    # Перебор групп и их команд
    for group_name, commands in commands_by_group.items():
        mmessage += f"\n**{group_name}:**\n"
        for command in commands:
            mmessage += f"  • {command}\n"

    return mmessage

def generate_commands_message_stud():
    commands_by_group = {
        "Основные команды": ["/start", "/help", "/view_class"],
        "Настройки": ["/admin_message", "/language"],
        "Дополнительные функции": ["/info", "/stats"]
    }

    # Начальная строка списка команд
    mmessagee = "Список доступных команд:\n"

    # Перебор групп и их команд
    for group_name, commands in commands_by_group.items():
        mmessagee += f"\n**{group_name}:**\n"
        for command in commands:
            mmessagee += f"  • {command}\n"

    return mmessagee



@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.DefaultState)
    user_id = message.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1:
        message_text = generate_commands_message()
        await message.answer(message_text)



        
        await message.answer("✅ Вы уже авторизованы как учитель." ,reply_markup=kb.back_role())
    else:
        await message.answer("👋 Привет! Выберите роль:", reply_markup=kb.role_selection_menu())


@router.callback_query(lambda c: c.data == "role_teacher")
async def role_teacher(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[0] == "teacher" and user[1] == 1:
        message_text = generate_commands_message()
        await callback.message.answer(message_text)


        await callback.message.answer("✅ Вы уже авторизованы как учитель.", reply_markup=kb.back_role())
    else:
        await callback.message.edit_text("📝 Введите логин и пароль в формате: логин пароль")
        await state.set_state(TeacherLogin.waiting_for_login)

@router.message(TeacherLogin.waiting_for_login)
async def check_teacher_login(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.ActiveState)
    user_id = message.from_user.id
    try:
        valid_login = "teacher"
        valid_password = "password"

        login, password = message.text.split()
        if login == valid_login and password == valid_password:
            conn = sqlite3.connect("users.db", isolation_level=None)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (user_id, role, is_authenticated) VALUES (?, ?, ?)",
                           (user_id, "teacher", 1))
            conn.commit()
            conn.close()
            await message.answer("🎉 Вы успешно авторизованы как учитель!")
            message_text = generate_commands_message()
            await message.answer(message_text)
            await state.clear()
            await state.set_state(UserStates.DefaultState)
        else:
            await message.answer("❌ Неверный логин или пароль. Попробуйте еще раз.", reply_markup=kb.role_selection_menu())
    except ValueError:
        await message.answer("⚠️ Введите данные в формате: логин пароль.", reply_markup=kb.role_selection_menu())

@router.callback_query(lambda c: c.data == "role_student")
async def role_student(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, role, is_authenticated) VALUES (?, ?, ?)",
                   (user_id, "student", 1))
    conn.commit()
    conn.close()
    message_text = generate_commands_message_stud()
    await callback.message.answer(message_text)
    await callback.message.answer("🎉 Вы успешно зарегистрированы как ученик!", reply_markup=kb.back_role())

@router.callback_query(lambda c: c.data == "exit_to_role")
async def exit_to_role(callback: types.CallbackQuery):
    await callback.message.answer("👋 Выберите роль:", reply_markup=kb.role_selection_menu())


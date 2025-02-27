import asyncio
import sqlite3
import app.keyboards as kb
import os

from werkzeug.security import generate_password_hash, check_password_hash
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
# from app.postGet import export_db_to_json, send_data_to_website

class TeacherLogin(StatesGroup):
    waiting_for_login = State()

    
router = Router()

def generate_commands_message():
    commands_by_group = {
        "Основные команды": ["/start", "/help", "/add_class"],
        "Настройки": ["/admin_message"],
        "Дополнительные функции": ["/info", "/stats"],
        "OwnerCmd": ["/helpp", "/TS"]
    }

    # Начальная строка списка команд
    mmessage = "Список доступных команд:\n"

    # Перебор групп и их команд
    for group_name, commands in commands_by_group.items():
        mmessage += f"\n**{group_name}:**\n"
        for command in commands:
            mmessage += f"  • {command}\n"

    return mmessage

def get_commands_message():
    commands_description = {
        "/start": "▶️ Запустить бота и начать работу.",
        "/help": "ℹ️ Получить dox file с доп. информацией.",
        "/add_class": "📚 Добавить новый класс.",
        "/admin_message": "🛠️ Отправить сообщение от администратора. OnlyAdmin",
        "/info": "📖 Узнать информацию о боте.",
        "/stats": "📈 Показать статистику.",
        "/helpp": "❓ Получить дополнительную помощь. OnlyAdmin",
        "/TS": "⚙️ Посмотреть технические данные. OnlyAdmin",
        "/send_Events": "🗓️ Отправить события пользователям.",
        "/view_class" : "📚 Просмотр расписания."
    }

    # Формируем текст сообщения
    response_message = "💡 *Доступные команды:*\n\n" + "\n".join([f"{cmd} – {desc}" for cmd, desc in commands_description.items()])

    return response_message



@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.DefaultState)
    user_id = message.from_user.id
    user_name = message.from_user.username
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name) VALUES (?, ?)", (user_id,user_name,))
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user and user[0] == "teacher" and user[1] == 1:
        response_message = get_commands_message()
        await message.answer(response_message)



        
        await message.answer("✅ Вы уже авторизованы как учитель." ,reply_markup=kb.back_role())
    else:
        await message.answer("👋 Привет! Выберите роль:", reply_markup=kb.role_selection_menu())

@router.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    await message.reply(f"Вся информация в ТГ канале бота.")
    await message.answer(f'https://t.me//NewsSchoolManager')


@router.callback_query(lambda c: c.data == "role_teacher")
async def role_teacher(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[0] == "teacher" and user[1] == 1:
        response_message = get_commands_message()
        await callback.message.answer(response_message)


        await callback.message.answer("✅ Вы уже авторизованы как учитель.", reply_markup=kb.back_role())
    else:
        await callback.message.edit_text(f"📝 Введите логин и пароль в формате: логин пароль\n\n\nДля отмены введите /notEnter")
        await state.set_state(TeacherLogin.waiting_for_login)

@router.message(TeacherLogin.waiting_for_login)
async def check_teacher_login(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.ActiveState)
    user_id = message.from_user.id

    if message.text == "/notEnter":
        await message.answer("❌ Регистрация отменена.", reply_markup=kb.role_selection_menu())
        await state.clear()
        await state.set_state(UserStates.DefaultState)
        return

    try:
        # Получаем логин и пароль из сообщения
        login, password = message.text.split(maxsplit=1)
        
        # Подключаемся к базе данных с учетными данными
        db_path = os.path.join('instance', 'site.db')
        conn_auth = sqlite3.connect(db_path)
        cursor_auth = conn_auth.cursor()
        
        # Ищем пользователя в базе
        cursor_auth.execute("SELECT password FROM user WHERE username = ?", (login,))
        auth_data = cursor_auth.fetchone()
        conn_auth.close()

        if not auth_data:
            await message.answer("❌ Пользователь не найден", reply_markup=kb.role_selection_menu())
            return

        # Проверяем пароль
        if check_password_hash(auth_data[0], password):
            # Подключаемся к основной базе пользователей
            conn_users = sqlite3.connect("users.db", isolation_level=None)
            cursor_users = conn_users.cursor()
            
            # Обновляем статус пользователя
            cursor_users.execute(
                "INSERT OR REPLACE INTO users (user_id, role, is_authenticated) VALUES (?, ?, ?)",
                (user_id, "teacher", 1)
            )
            conn_users.commit()
            conn_users.close()

            await message.answer("🎉 Вы успешно авторизованы как учитель!")
            response_message = get_commands_message()
            await message.answer(response_message)
        else:
            await message.answer("❌ Неверный логин или пароль", reply_markup=kb.role_selection_menu())

    except ValueError:
        await message.answer("⚠️ Введите данные в формате: логин пароль", reply_markup=kb.role_selection_menu())
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        await message.answer("⚠️ Произошла ошибка авторизации", reply_markup=kb.role_selection_menu())
    finally:
        await state.clear()
        await state.set_state(UserStates.DefaultState)

@router.callback_query(lambda c: c.data == "role_student")
async def role_student(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT role, is_authenticated, class_id FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if (
        user  # проверяем, что запись существует
        and user[0]  # проверяем, что role существует и не пустой
        and user[1] == 1  # проверяем, что is_authenticated равен 1
        and user[2] is not None  # проверяем, что class_id не NULL
        and user[0] == "student"  # проверяем, что role равен "student"
    ):
        response_message = get_commands_message()
        await callback.message.answer(response_message)
        await callback.message.answer(
            f"✅ Вы уже авторизованы как студент.\n Ваш класс {user[2]}", 
            reply_markup=kb.back_role_2()
        )
    else:
        conn = sqlite3.connect("users.db", isolation_level=None)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, role, is_authenticated) VALUES (?, ?, ?)",
                   (user_id, "student", 1))
        conn.commit()
        conn.close()
        await callback.message.answer("В каком вы классе учитесь?\nЕсли его нет, значит его не создал учитель.", reply_markup=kb.generate_class_menu())


@router.callback_query(lambda c: c.data == "change_classssss")
async def chanhe_classss(callback: types.CallbackQuery):
    await callback.message.answer("В каком вы классе учитесь?\nЕсли его нет, значит его не создал учитель.", reply_markup=kb.back_3())



@router.callback_query(lambda c: c.data == "exit_to_role")
async def exit_to_role(callback: types.CallbackQuery):
    await callback.message.answer("👋 Выберите роль:", reply_markup=kb.role_selection_menu())

@router.callback_query(lambda c: c.data.startswith("select_class_"))
async def select_class(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    class_id = callback.data.split("_")[2]

    # Update the user's class_id in users.db
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET class_id = ? WHERE user_id = ?", (class_id, user_id)
    )
    conn.commit()
    conn.close()

    await callback.message.answer(f"Вы записаны в класс с ID: {class_id}.")
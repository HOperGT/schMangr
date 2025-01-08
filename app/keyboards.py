import json
import sqlite3
import time

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton 
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def role_selection_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👩‍🏫 Учитель", callback_data="role_teacher")
    builder.button(text="👦 Ученик", callback_data="role_student")
    builder.button(text="Новостной канал бота", url="https://t.me//NewsSchoolManager")
    builder.adjust(2)
    return builder.as_markup()


def back_role() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Выйти", callback_data="exit_to_role"))
    builder.adjust(1)
    return builder.as_markup()


def student_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📅 Расписание", callback_data="schedule"))
    builder.add(InlineKeyboardButton(text="🎉 Мероприятия", callback_data="events"))
    builder.add(InlineKeyboardButton(text="📰 Новости", callback_data="news"))
    builder.add(InlineKeyboardButton(text="🔙 Выйти", callback_data="exit_to_role"))
    builder.adjust(2)
    return builder.as_markup()


# # Функция для генерации клавиатуры
# def generate_main_menu() -> InlineKeyboardMarkup:
#     # Создаем объект InlineKeyboardBuilder
#     builder = InlineKeyboardBuilder()

#     # Берем кнопки из базы данных
#     cursor.execute("SELECT ID FROM subject")
#     buttons = cursor.fetchall()

#     # Добавляем пользовательские кнопки
#     for button_name in buttons:
#         builder.button(
#             text=button_name[0],  # Название кнопки
#             callback_data=f"button:{button_name[0]}"  # Данные колбэка
#         )

#     # Добавляем кнопки "Добавить" и "Удалить"
    

#     builder.button(text="➕ Добавить кнопку", callback_data="add_button")
#     builder.button(text="➖ Удалить кнопку", callback_data="delete_button")
#     builder.button(text="🔙 Вернуться", callback_data="menu_class")
#     builder.adjust(2)
#     # Настраиваем клавиатуру, чтобы кнопки располагались по одной в строке
    

#     return builder.as_markup()



def class_menu():
    # Создание объекта WebAppInfo
    web_app_info = WebAppInfo(url='https://webappsch-hoper.amvera.io/')

    # Создание клавиатуры
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Открыть веб-приложение", web_app=web_app_info))
    return builder.as_markup(resize_keyboard=True)

    
    
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
    builder.button(text="Поддержка", url="https://t.me/helpBotSchoolManager_bot")
    builder.adjust(2)
    return builder.as_markup()


def back_role() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Выйти", callback_data="exit_to_role"))
    builder.button(text="Поддержка", url="https://t.me/helpBotSchoolManager_bot")
    builder.adjust(1)
    return builder.as_markup()

def back_role_2() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Выйти", callback_data="exit_to_role"))
    builder.add(InlineKeyboardButton(text="🔙 Сенить класс", callback_data="change_classssss"))
    builder.button(text="Поддержка", url="https://t.me/helpBotSchoolManager_bot")
    builder.adjust(1)
    return builder.as_markup()

def back_3() -> InlineKeyboardMarkup:
    
    builder = InlineKeyboardBuilder()

    
    conn_classes = sqlite3.connect("instance/site.db", isolation_level=None)
    cursor_classes = conn_classes.cursor()
    cursor_classes.execute("SELECT id, class_name FROM class_schedule")
    class_buttons = cursor_classes.fetchall()
    conn_classes.close()

    
    for class_id, class_name in class_buttons:
        builder.button(
            text=class_name,  
            callback_data=f"select_class_{class_name}"  
        )

    
    builder.button(text="🔙 Вернуться", callback_data="exit_to_role")
    builder.add(InlineKeyboardButton(text="Не менять класс.", callback_data="role_student"))
    builder.adjust(1)  

    return builder.as_markup()  


def student_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📅 Расписание", callback_data="schedule"))
    builder.add(InlineKeyboardButton(text="🎉 Мероприятия", callback_data="events"))
    builder.add(InlineKeyboardButton(text="📰 Новости", callback_data="news"))
    builder.add(InlineKeyboardButton(text="🔙 Выйти", callback_data="exit_to_role"))
    builder.button(text="Поддержка", url="https://t.me/helpBotSchoolManager_bot")
    builder.adjust(2)
    return builder.as_markup()


def generate_class_menu() -> InlineKeyboardMarkup:
    
    builder = InlineKeyboardBuilder()

    
    conn_classes = sqlite3.connect("instance/site.db", isolation_level=None)
    cursor_classes = conn_classes.cursor()
    cursor_classes.execute("SELECT id, class_name FROM class_schedule")
    class_buttons = cursor_classes.fetchall()
    conn_classes.close()

    
    for class_id, class_name in class_buttons:
        builder.button(
            text=class_name,  
            callback_data=f"select_class_{class_name}"  
        )

    
    builder.button(text="🔙 Вернуться", callback_data="exit_to_role")

    builder.adjust(1) 

    return builder.as_markup() 

def generate_sendmessclass() -> InlineKeyboardMarkup:
    
    builder = InlineKeyboardBuilder()

    
    conn_classes = sqlite3.connect("instance/site.db", isolation_level=None)
    cursor_classes = conn_classes.cursor()
    cursor_classes.execute("SELECT id, class_name FROM class_schedule")
    class_buttons = cursor_classes.fetchall()
    conn_classes.close()

    
    for class_id, class_name in class_buttons:
        builder.button(
            text=class_name,  
            callback_data=f"view_{class_name}"  
        )

    
    builder.button(text="🔙 Вернуться", callback_data="exit_to_role")

    builder.adjust(1)  

    return builder.as_markup()  




def class_menu():
    
    web_app_info = WebAppInfo(url='https://webappsch-hoper.amvera.io/')

    
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Открыть веб-приложение", web_app=web_app_info))
    return builder.as_markup(resize_keyboard=True)

    
def choose_view() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отправить всем ученикам.", callback_data="all_send"))
    builder.add(InlineKeyboardButton(text="Отправить классу.", callback_data="send_choose"))
    builder.adjust(1)
    return builder.as_markup()    
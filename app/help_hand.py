import asyncio
import os
import sqlite3
import time
import app.keyboards as kb
import json
import requests
from aiogram.types import FSInputFile
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
from config import OWNER_TELEGRAM_ID, TOKEN

bot = Bot(token=TOKEN)
router_help= Router()
class FileUploadState(StatesGroup):
    waiting_for_file = State()

@router_help.message(Command("help"))
async def help_command(message: types.Message):
    file_path = 'data/helping.docx'  # Укажите путь к вашему файлу
    if os.path.exists(file_path):
        document = FSInputFile(file_path)  # Используем FSInputFile для указания локального файла
        await message.answer_document(document)
    else:
        await message.answer("Файл помощи не найден.")


@router_help.message(Command("helpp"))
async def helpp_command(message: types.Message, state: FSMContext):
    if message.from_user.id == OWNER_TELEGRAM_ID:  # Проверяем, является ли отправитель администратором
        await message.answer("Отправьте файл Word (в формате .docx), который нужно загрузить в систему.\n\nДля отмены введите /notSend")
        await state.set_state(FileUploadState.waiting_for_file)
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")        


@router_help.message(FileUploadState.waiting_for_file)
async def document_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == OWNER_TELEGRAM_ID:

        if message.text == '/notSend':
            await message.answer(f"Отмена операции отправки file help.docx!")
            await state.clear()
            return  
        
        document = message.document
        if document.file_name.endswith('.docx'):  # Проверяем, является ли файл форматом .docx
            file_path = 'data/helping.docx'  # Указываем, что файл будет сохранен как helping.docx
            file = await bot.get_file(document.file_id)  # Скачиваем файл
            with open(file_path, 'wb') as f:
                await bot.download_file(file.file_path, file_path) # Сохраняем файл в систему
            await message.answer("Файл успешно загружен в систему и сохранен как data/helping.docx")
            await state.clear() # Завершаем состояние
        else:
            await message.answer("Пожалуйста, загрузите файл в формате .docx")
    else:
        await message.answer("У вас нет прав для загрузки документов.")
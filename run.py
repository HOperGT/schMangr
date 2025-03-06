import datetime
import json
import logging
import os
import sqlite3
import asyncio
from flask import jsonify, request
import requests
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from config import TOKEN 
from app.handlers_stud import router_stud
from app.handlers import router
from app.handlers_teacher import router_tech
from app.funny_handlers import  router_funny
from app.hoper_handlers import routerHP
from app.help_hand import router_help


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
stats = {
    "start_time": datetime.datetime.now(),
    "inline_queries": 0,  
}

@dp.message(Command('stats'))
async def stats_command(message: types.Message):
    
    uptime = datetime.datetime.now() - stats["start_time"]
    stats_report = (
        f"⏳ Время работы бота: {uptime}\n"
        
    )
    await message.answer(stats_report)



async def init_db():
    conn = sqlite3.connect("users.db", isolation_level=None)
    cursor = conn.cursor()

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT,       
            role TEXT,
            is_authenticated INTEGER DEFAULT 0,
            class_id TEXT DEFAULT NULL
        )
    """)
    
    conn.commit()
    conn.close()


class TeacherLogin(StatesGroup):
    waiting_for_login = State()

# async def delete_webhook(bot: Bot):
#     try:
#         await bot.delete_webhook()
#         print("Webhook successfully deleted")
#     except ValueError:
#         print("Webhook already deleted or not set")

# DB_FILE = 'users.db'
# JSON_FILE = 'uploaded_data.json'
# UPLOAD_URL = "https://webappsch-hoper.amvera.io/upload"

# async def export_db_to_json():
#     conn = sqlite3.connect('users.db')
#     cursor = conn.cursor()
    
#     
#     cursor.execute('SELECT user_id, role FROM users')
#     rows = cursor.fetchall()

#     
#     data = [{"id": row[0], "role": row[1]} for row in rows]

#     
#     with open('uploaded_data.json', 'w') as json_file:
#         json.dump(data, json_file, indent=4)

#     conn.close()

# async def send_data_to_website():
#     try:
#             url = "https://webappsch-hoper.amvera.io/upload"  
#          
#             with open('uploaded_data.json', 'rb') as file:
#                 files = {'file': file}
#                 response = requests.post(url, files=files)

#             if response.status_code == 200:
#                 print("Данные успешно отправлены на сайт")
#             else:
#                 print(f"Ошибка: {response.status_code}")
#     except requests.exceptions.ConnectionError:
#         print('url, не отвечает!')    




# async def background_tasks():
#     while True:
#         await export_db_to_json()
#         # await send_data_to_website()
#         await asyncio.sleep(10) 



async def main():
    dp.include_router(router)
    dp.include_router(router_tech)
    dp.include_router(router_stud)
    dp.include_router(router_help)
    #dp.include_router(router_funny)
    dp.include_router(routerHP)
    # dp.include_router(router_gr)
   
    # asyncio.create_task(background_tasks())
    
    await init_db()
    # await delete_webhook(bot)
    await dp.start_polling(bot)


# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Exit")        
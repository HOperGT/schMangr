import asyncio
from threading import Thread
from appw import app
from run import main as run_bot

# Функция для запуска Flask
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Функция для запуска бота в отдельном потоке
def run_bot_forever():
    asyncio.run(run_bot())  # Используем asyncio.run для запуска корутины

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Запускаем бота в основном потоке
    run_bot_forever()
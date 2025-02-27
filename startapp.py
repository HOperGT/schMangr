import asyncio
from threading import Thread

from waitress import serve
from appw import app
from run import main as run_bot


def run_flask():
    serve(app, host='0.0.0.0', port=8080, threads=4)
    #app.run(host='0.0.0.0', port=8080, threads=4)
    #app.run(host='0.0.0.0', port=5000)
# отдельный поток
def run_bot_forever():
    asyncio.run(run_bot())  

if __name__ == '__main__':
    
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    
    run_bot_forever()
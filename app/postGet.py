import json
import sqlite3
import requests


def export_db_to_json():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Изменяем SQL запрос, чтобы получить и user_id, и role
    cursor.execute('SELECT user_id, role FROM users')
    rows = cursor.fetchall()

    # Конвертация данных в список словарей с id и role
    data = [{"id": row[0], "role": row[1]} for row in rows]

    # Сохранение данных в JSON-файл
    with open('uploaded_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    conn.close()



def send_data_to_website():
    try:
            url = "http://192.168.155.148:8080/upload"  # URL сайта, принимающего данные
         # Загрузка локального JSON файла
            with open('uploaded_data.json', 'rb') as file:
                files = {'file': file}
                response = requests.post(url, files=files)

            if response.status_code == 200:
                print("Данные успешно отправлены на сайт")
            else:
                print(f"Ошибка: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print('url, не отвечает!')    
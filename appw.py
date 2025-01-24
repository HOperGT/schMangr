import asyncio
import json
import sqlite3
import time
from flask_cors import CORS
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
from waitress import serve
from flask_talisman import Talisman
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "y93=t6l_(o)-=7%@=!$7@*vrj#_i((s0=n*4*i+k254ubh&1np"
db = SQLAlchemy(app)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ClassSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    monday = db.Column(db.String(500), default="")
    tuesday = db.Column(db.String(500), default="")
    wednesday = db.Column(db.String(500), default="")
    thursday = db.Column(db.String(500), default="")
    friday = db.Column(db.String(500), default="")
    saturday = db.Column(db.String(500), default="")
    sunday = db.Column(db.String(500), default="")

with app.app_context():
    db.create_all()

@app.route('/menu')
def index():
    classes = ClassSchedule.query.all()
    return render_template('index.html', classes=classes)

@app.route('/menuSt')
def indexSt():
    classes = ClassSchedule.query.all()
    return render_template('viewStud.html', classes=classes)

@app.route('/viewStud/<int:id>', methods=['GET', 'POST'])
def view_schedule(id):
    class_schedule = ClassSchedule.query.get_or_404(id)
    if request.method == 'POST':
        class_schedule.monday = ','.join(request.form.getlist('monday'))
        class_schedule.tuesday = ','.join(request.form.getlist('tuesday'))
        class_schedule.wednesday = ','.join(request.form.getlist('wednesday'))
        class_schedule.thursday = ','.join(request.form.getlist('thursday'))
        class_schedule.friday = ','.join(request.form.getlist('friday'))
        class_schedule.saturday = ','.join(request.form.getlist('saturday'))
        class_schedule.sunday = ','.join(request.form.getlist('sunday'))
        db.session.commit()
        return redirect(url_for('viewStud'))
    return render_template('view_shedule.html', class_schedule=class_schedule)

@app.route('/', methods=['GET', 'POST'])
def index2():
    classes = ClassSchedule.query.all()

    if request.method == 'POST':
        user_input = request.form.get('number')

        if user_input:
            try:
                conn = sqlite3.connect("users.db", isolation_level=None)
                cursor = conn.cursor()

                # Выполняем запрос
                cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_input,))
                user = cursor.fetchone()
                conn.close()

                # Отладочная печать
                print("Полученный пользователь:", user)

                # Проверяем роль
                if user and user[0].strip().lower() == "teacher":
                    return render_template('index.html', classes=classes)
                else:
                    flash("Доступ запрещен! Необходимы права учителя!")

            except ValueError:
                flash("Введите корректное число!")

    return render_template('index2.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        class_name = request.form['class_name']

        # Проверка на существование класса с таким же именем
        existing_class = ClassSchedule.query.filter_by(class_name=class_name).first()
        if existing_class:
            # Если класс существует, возвращаем сообщение об ошибке
            error_message = "Ошибка: класс с таким именем уже существует."
            return render_template('register.html', error=error_message)

        # Создание и сохранение нового класса
        new_class = ClassSchedule(class_name=class_name)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/add_schedule/<int:id>', methods=['GET', 'POST'])
def add_schedule(id):
    class_schedule = ClassSchedule.query.get_or_404(id)
    if request.method == 'POST':
        class_schedule.monday = ','.join(request.form.getlist('monday'))
        class_schedule.tuesday = ','.join(request.form.getlist('tuesday'))
        class_schedule.wednesday = ','.join(request.form.getlist('wednesday'))
        class_schedule.thursday = ','.join(request.form.getlist('thursday'))
        class_schedule.friday = ','.join(request.form.getlist('friday'))
        class_schedule.saturday = ','.join(request.form.getlist('saturday'))
        class_schedule.sunday = ','.join(request.form.getlist('sunday'))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_schedule.html', class_schedule=class_schedule)


@app.route('/delete_class_by_name', methods=['POST'])
def delete_class_by_name():
    class_name = request.form['class_name']
    class_to_delete = ClassSchedule.query.filter_by(class_name=class_name).first()
    
    if class_to_delete:
        db.session.delete(class_to_delete)
        db.session.commit()
        
    
    return redirect(url_for('index'))





@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    # Получаем данные формы
    monday = request.form.getlist('monday')
    tuesday = request.form.getlist('tuesday')
    wednesday = request.form.getlist('wednesday')
    thursday = request.form.getlist('thursday')
    friday = request.form.getlist('friday')
    saturday = request.form.getlist('saturday')
    sunday = request.form.getlist('sunday')

    # Считаем идентификатор класса (например, передаем его как параметр в форме)
    class_id = request.form.get('class_id')  # Добавьте этот параметр в форму

    # Находим расписание в базе данных
    class_schedule = ClassSchedule.query.get_or_404(class_id)

    # Обновляем расписание с новыми значениями
    class_schedule.monday = ','.join(monday)
    class_schedule.tuesday = ','.join(tuesday)
    class_schedule.wednesday = ','.join(wednesday)
    class_schedule.thursday = ','.join(thursday)
    class_schedule.friday = ','.join(friday)
    class_schedule.saturday = ','.join(saturday)
    class_schedule.sunday = ','.join(sunday)

    # Сохраняем изменения в базе данных
    db.session.commit()

    return '', 204  # Успешный ответ без содержимого
def get_class_name(class_id):
    with sqlite3.connect('instance/classes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT class_name FROM class_schedule WHERE id = ?", (class_id,))
        class_name_row = cursor.fetchone()
        if class_name_row:
            return class_name_row[0]
        else:
            return None

def get_users_by_class_id(class_id):
    class_name = get_class_name(class_id)
    if not class_name:
        return []  # Возвращаем пустой список, если class_name не найден

    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE class_id = ?", (class_name,))
        users = cursor.fetchall()
        
        return [{'telegram_id': user[0]} for user in users]

@app.route('/send_schedule/<int:class_id>', methods=['POST'])
def send_schedule(class_id):
    try:
        data = request.get_json()
        schedule = data.get('schedule')
        lessons = schedule.get('lessons', [])
        date = schedule.get('date')
        schedule_id = schedule.get('schedule_id')
        class_name = get_class_name(schedule_id)  # Ваша функция получения названия класса
        users = get_users_by_class_id(schedule_id)
        print(f"Полученные данные: {schedule}")  # Ваша функция получения пользователей

        lesson_data = {}
        for lesson in lessons:
            lesson_data[lesson.get('lesson_number')] = {
                'time': lesson.get('time'),
                'lesson': lesson.get('lesson', '-'),
                'classroom': lesson.get('classroom', '-') #  Добавляем кабинет
            }

        message = f"Расписание для класса {class_name} на {date}:\n\n" # Добавлено \n\n для отступа

        for i in range(1, 9):
            lesson_info = lesson_data.get(i, {'time': '-', 'lesson': '-', 'classroom': '-'})
            message += f"Урок {i}:\n"
            message += f"  Время: {lesson_info['time']}\n"
            message += f"  Предмет: {lesson_info['lesson']}\n"
            message += f"  Кабинет: {lesson_info['classroom']}\n\n" # Добавлено \n\n для отступа


        for user in users:
            send_message_to_telegram(user['telegram_id'], message) # Ваша функция отправки в Telegram

        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'success': False})

def send_message_to_telegram(telegram_id, message):
    url = f'https://api.telegram.org/bot7995834848:AAH4d_aDCh5LXPBE3NB2QPDCy5xdLZ1BC5s/sendMessage'
    data = {
        'chat_id': telegram_id,
        'text': str(message),
    }
    requests.post(url, json=data)



if __name__ == '__main__':
    # Настройка логирования (опционально)
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    print("Starting server on !!")
    app.run(host='0.0.0.0', port=8080, debug=True)
    #serve(app, host='0.0.0.0', port=8080, threads=4)
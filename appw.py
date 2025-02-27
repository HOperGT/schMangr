import asyncio
import json
import sqlite3
import time
from config import TOKEN
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve
from flask_talisman import Talisman
import os


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "y93=t6l_(o)-=7%@=!$7@*vrj#_i((s0=n*4*i+k254ubh&1np"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
CORS(app)
# csrf = CSRFProtect(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)
    logged_in = db.Column(db.Boolean, default=False)


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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin'))
            else:
                user.logged_in = True
                db.session.commit()
                return redirect(url_for('user_page'))
        else:
            flash('Неверный логин или пароль')
    return render_template('login.html')


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    admin_user = User.query.get(session['user_id'])
    if not admin_user.is_admin:
        return redirect(url_for('index'))
    
    user_to_delete = User.query.get(user_id)
    if not user_to_delete:
        flash('Пользователь не найден', 'danger')
    else:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('Пользователь успешно удалён', 'success')
    
    return redirect(url_for('admin'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    admin_user = User.query.get(session['user_id'])
    if not admin_user.is_admin:
        return redirect(url_for('index2'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Этот логин уже занят!')
        elif password != confirm_password:
            flash('Пароли не совпадают!')
        else:
            hashed_password = generate_password_hash(password)
            new_teacher = User(
                username=username,
                password=hashed_password,
                is_teacher=True
            )
            db.session.add(new_teacher)
            db.session.commit()
            flash('Учитель успешно создан!')
    
    teachers = User.query.filter_by(is_teacher=True).all()
    return render_template('admin.html', teachers=teachers)

# with app.app_context():
#     user = User(username="", password=generate_password_hash(""), is_admin=True)
#     db.session.add(user)
#     db.session.commit()


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index12'))

@app.route('/')
def index12():
    return render_template('index2.html')




@app.route('/menu')
def user_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    classes = ClassSchedule.query.all()
    return render_template('index.html', classes=classes)





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        class_name = request.form['class_name']

        
        existing_class = ClassSchedule.query.filter_by(class_name=class_name).first()
        if existing_class:
            
            error_message = "Ошибка: класс с таким именем уже существует."
            return render_template('register.html', error=error_message)

        
        new_class = ClassSchedule(class_name=class_name)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('user_page'))

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
        return redirect(url_for('user_page'))
    return render_template('add_schedule.html', class_schedule=class_schedule)


@app.route('/delete_class_by_name', methods=['POST'])
def delete_class_by_name():
    class_name = request.form['class_name']
    class_to_delete = ClassSchedule.query.filter_by(class_name=class_name).first()
    
    if class_to_delete:
        db.session.delete(class_to_delete)
        db.session.commit()
        
    
    return redirect(url_for('user_page'))





@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    
    monday = request.form.getlist('monday')
    tuesday = request.form.getlist('tuesday')
    wednesday = request.form.getlist('wednesday')
    thursday = request.form.getlist('thursday')
    friday = request.form.getlist('friday')
    saturday = request.form.getlist('saturday')
    sunday = request.form.getlist('sunday')

    
    class_id = request.form.get('class_id')  

    
    class_schedule = ClassSchedule.query.get_or_404(class_id)

    
    class_schedule.monday = ','.join(monday)
    class_schedule.tuesday = ','.join(tuesday)
    class_schedule.wednesday = ','.join(wednesday)
    class_schedule.thursday = ','.join(thursday)
    class_schedule.friday = ','.join(friday)
    class_schedule.saturday = ','.join(saturday)
    class_schedule.sunday = ','.join(sunday)

    
    db.session.commit()

    return '', 204  
def get_class_name(class_id):
    with sqlite3.connect('instance/site.db') as conn:
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
        return [] 

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
        class_name = get_class_name(schedule_id)  
        users = get_users_by_class_id(schedule_id)
        print(f"Полученные данные: {schedule}") 

        lesson_data = {}
        for lesson in lessons:
            lesson_data[lesson.get('lesson_number')] = {
                'time': lesson.get('time'),
                'lesson': lesson.get('lesson', '-'),
                'classroom': lesson.get('classroom', '-') 
            }

        message = f"Расписание для класса {class_name} на {date}:\n\n" 

        for i in range(1, 9):
            lesson_info = lesson_data.get(i, {'time': '-', 'lesson': '-', 'classroom': '-'})
            message += f"Урок {i}:\n"
            message += f"  Время: {lesson_info['time']}\n"
            message += f"  Предмет: {lesson_info['lesson']}\n"
            message += f"  Кабинет: {lesson_info['classroom']}\n\n" 
            

        for user in users:
            send_message_to_telegram(user['telegram_id'], message) 

        return jsonify({'success': True})
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'success': False})

def send_message_to_telegram(telegram_id, message):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': telegram_id,
        'text': str(message),
    }
    requests.post(url, json=data)



if __name__ == '__main__':
    
    import logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    
    print("Starting server on !!")
    #app.run(host='0.0.0.0', port=5000)
    serve(app, host='0.0.0.0', port=8080, threads=4)
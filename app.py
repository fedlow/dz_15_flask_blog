from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps

app = Flask(__name__)

# --- Настройки БД и Секретного ключа (для токенов) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key-change-me-in-production' # Обязательно для сессий!

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Модели ---
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# --- Работа с токенами ---
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_token(username):
    # Генерируем токен на основе логина
    return serializer.dumps(username, salt='auth-token')

def verify_token(token, max_age=3600):
    # Проверяем токен (по умолчанию живет 1 час = 3600 сек)
    try:
        username = serializer.loads(token, salt='auth-token', max_age=max_age)
        return username
    except:
        return None

# --- Декоратор для защиты страниц ---
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        
        if not token:
            flash('Пожалуйста, войдите в систему.', 'warning')
            return redirect(url_for('login'))
            
        username = verify_token(token)
        if not username:
            session.pop('token', None) # Удаляем просроченный токен
            flash('Сессия истекла. Пожалуйста, войдите снова.', 'danger')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

# --- Маршруты ---

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
@token_required
def index():
    return render_template('index.html')

@app.route('/notes', methods=['GET', 'POST'])
@token_required
def notes():
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        
        if title and content:
            new_note = Notes(title=title, subtitle=subtitle, text=content)
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('notes'))
    
    all_notes = Notes.query.order_by(Notes.id.desc()).all()
    return render_template('notes.html', notes=all_notes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Проверка, существует ли уже такой пользователь
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Пользователь с таким логином или email уже существует.', 'danger')
            return redirect(url_for('register'))
            
        # Хешируем пароль и сохраняем
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь войдите.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Ошибка при регистрации.', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        # Проверяем существование пользователя и правильность пароля
        if not user or not check_password_hash(user.password, password):
            flash('Неверный логин или пароль.', 'danger')
            return redirect(url_for('login'))
            
        # Генерируем токен и сохраняем в сессию
        token = generate_token(user.username)
        session['token'] = token
        session['username'] = user.username
        
        flash('Вы успешно вошли!', 'success')
        return redirect(url_for('index')) # Перенаправление на главную
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('username', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
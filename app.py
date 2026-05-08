import os
from flask import Flask, redirect, render_template, request, session, url_for
import requests
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'j5k9$mP2#vL8*nQ4@xR7&wT3^yF6'

API_KEY = 'ndh_UpMMdPtS-8b9Tn29ZeRVLlWsfQpG37LHDRckz7YYncw'

DATABASE_PATH = os.path.join('db', 'database.db')

def get_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "users" (
            "id" INTEGER,
            "username" TEXT NOT NULL,
            "email" TEXT NOT NULL,
            "password" TEXT NOT NULL,
            "language" TEXT NOT NULL DEFAULT 'en',
            "country" TEXT,
            "api" TEXT,
            "api_provider" TEXT NOT NULL DEFAULT 'groq' CHECK("api_provider" IN ('openai', 'google', 'groq')),
            "role" TEXT NOT NULL DEFAULT 'user',
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("id")
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/dashboard')
@login_required
def dashboard():
    topic = request.args.get('topic', 'technology')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    user_language = user['language'] if user else 'en'
    
    try:
        response = requests.get(
            'https://api.newsdatahub.com/v1/news',
            headers={
                'X-API-Key': API_KEY,
                'User-Agent': 'marketing-free-news-api/1.0-py'
            },
            params={
                'topic': topic,
                'language': user_language,
                'per_page': 6
            },
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        articles = data.get('data', [])
        
    except Exception as e:
        articles = []
        error = f"Error fetching news: {str(e)}"
        return render_template('dashboard.html', articles=articles, error=error)
    
    return render_template('dashboard.html', articles=articles, error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        
        return render_template("auth/login.html", error="Invalid email or password")
    
    return render_template("auth/login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        language = request.form.get('language', 'en')
        country = request.form.get('country')
        api = request.form.get('api')
        api_provider = request.form.get('api_provider', 'groq')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return render_template("auth/register.html", error="Email already registered")
        
        cursor.execute("""
            INSERT INTO users (username, email, password, language, country, api, api_provider)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, email, hashed_password, language, country, api, api_provider))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        
        return redirect(url_for('dashboard'))
    
    return render_template("auth/register.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
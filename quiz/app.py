from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode
from datetime import datetime
import sqlite3
import json
import os
import socket

app = Flask(__name__)

# Create necessary directories
def create_directories():
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')

# Get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return '127.0.0.1'

# Create database and tables
def init_db():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (name TEXT, score INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

# Quiz questions - full 10 questions
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct": 2
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": 1
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo"],
        "correct": 1
    },
    {
        "question": "What is the largest organ in the human body?",
        "options": ["Heart", "Brain", "Liver", "Skin"],
        "correct": 3
    },
    {
        "question": "Which element has the chemical symbol 'O'?",
        "options": ["Gold", "Oxygen", "Osmium", "Oganesson"],
        "correct": 1
    },
    {
        "question": "In which year did World War II end?",
        "options": ["1943", "1944", "1945", "1946"],
        "correct": 2
    },
    {
        "question": "What is the smallest prime number?",
        "options": ["0", "1", "2", "3"],
        "correct": 2
    },
    {
        "question": "Which country is home to the kangaroo?",
        "options": ["New Zealand", "South Africa", "Australia", "Brazil"],
        "correct": 2
    },
    {
        "question": "What is the hardest natural substance on Earth?",
        "options": ["Gold", "Iron", "Diamond", "Platinum"],
        "correct": 2
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "correct": 1
    }
]

# Generate QR Code
def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_path = os.path.join(os.getcwd(), 'static', 'qr_code.png')
    qr_image.save(qr_path)
    print(f"QR Code saved to: {qr_path}")
    return url

@app.route('/')
def index():
    local_ip = get_local_ip()
    quiz_url = f'http://{local_ip}:5000/quiz'
    return render_template('index.html', quiz_url=quiz_url)

@app.route('/quiz')
def quiz():
    questions_json = json.dumps(QUESTIONS).replace("'", "\\'").replace('"', '\\"')
    return render_template('quiz.html', questions=questions_json)
@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    name = data.get('name')
    score = data.get('score')
    
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute("INSERT INTO scores (name, score, timestamp) VALUES (?, ?, ?)",
              (name, score, datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('quiz.db')
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC, timestamp DESC LIMIT 10")
    leaders = c.fetchall()
    conn.close()
    return render_template('leaderboard.html', leaders=leaders)

if __name__ == '__main__':
    create_directories()
    local_ip = get_local_ip()
    print(f"Local IP Address: {local_ip}")
    quiz_url = f'http://{local_ip}:5000/quiz'
    generate_qr(quiz_url)
    print("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
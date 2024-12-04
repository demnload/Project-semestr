from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    with sqlite3.connect('planner.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL
            )
        ''')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    with sqlite3.connect('planner.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
    return jsonify(tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        with sqlite3.connect('planner.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task not specified!'}), 400

@app.route('/edit_task', methods=['POST'])
def edit_task():
    task_id = request.form.get('task_id')
    new_task = request.form.get('task')
    if task_id and new_task:
        with sqlite3.connect('planner.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE tasks SET task = ? WHERE id = ?', (new_task, task_id))
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task ID or task text missing!'}), 400

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = request.form.get('task_id')
    if task_id:
        with sqlite3.connect('planner.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task ID missing!'}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

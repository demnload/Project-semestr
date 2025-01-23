from flask import Flask, render_template, request, jsonify
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit TEXT NOT NULL,
                completed BOOLEAN NOT NULL CHECK (completed IN (0, 1))
            )
        ''')

@app.route('/get_habits', methods=['GET'])
def get_habits():
    with sqlite3.connect('planner.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM habits')
        habits = cursor.fetchall()
    return jsonify(habits)

@app.route('/add_habit', methods=['POST'])
def add_habit():
    habit = request.form.get('habit')
    if habit:
        with sqlite3.connect('planner.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO habits (habit, completed) VALUES (?, ?)', (habit, 0))
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Habit not specified!'}), 400

@app.route('/toggle_habit/<int:habit_id>', methods=['POST'])
def toggle_habit(habit_id):
    with sqlite3.connect('planner.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT completed FROM habits WHERE id = ?', (habit_id,))
        habit = cursor.fetchone()
        if habit:
            new_status = 1 - habit[0]  # Переключаем статус
            cursor.execute('UPDATE habits SET completed = ? WHERE id = ?', (new_status, habit_id))
            return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Habit not found!'}), 404

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

notes = []

@app.route('/add_note', methods=['POST'])
def add_note():
    note = request.form.get('note')
    if note:
        notes.append(note)
        return jsonify({'success': True, 'message': 'Заметка добавлена'})
    return jsonify({'success': False, 'error': 'Текст заметки отсутствует'}), 400

@app.route('/get_notes', methods=['GET'])
def get_notes():
    return jsonify([[index, note] for index, note in enumerate(notes)])

@app.route('/edit_note', methods=['POST'])
def edit_note():
    try:
        note_index = int(request.form.get('note_index'))
        new_note = request.form.get('note')
        if 0 <= note_index < len(notes) and new_note:
            notes[note_index] = new_note
            return jsonify({'success': True, 'message': f'Заметка обновлена: "{new_note}"'})
        return jsonify({'success': False, 'error': 'Неверный индекс заметки или пустой текст'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Индекс заметки должен быть числом'}), 400

@app.route('/delete_note', methods=['POST'])
def delete_note():
    try:
        note_index = int(request.form.get('note_index'))
        if 0 <= note_index < len(notes):
            deleted_note = notes.pop(note_index)
            return jsonify({'success': True, 'message': f'Заметка "{deleted_note}" удалена'})
        return jsonify({'success': False, 'error': 'Неверный индекс заметки'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Индекс заметки должен быть числом'}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
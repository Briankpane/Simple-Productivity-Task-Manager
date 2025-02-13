from flask import Flask, render_template, request, redirect, url_for
import json


app = Flask(__name__)

# Load tasks from JSON file
def load_tasks():
    try:
        with open('tasks.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save tasks to JSON file
def save_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file, indent=4)

# Homepage - Display tasks
@app.route('/')
def home():
    tasks = load_tasks()
    sort_by = request.args.get('sort')
    if sort_by == 'priority':
        # Define a mapping so that High > Medium > Low
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        # Use .capitalize() in case the task's priority is not capitalized consistently
        tasks.sort(key=lambda task: priority_order.get(task.get('priority', 'Low').capitalize(), 0), reverse=True)
    return render_template('index.html', tasks=tasks)


# Add a task with due date, priority, empty writing, and timer initialized to 0
@app.route('/add', methods=['POST'])
def add_task():
    task_text = request.form.get('task')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority', 'Medium')  # Default to Medium if not provided

    if not task_text or not due_date:
        return redirect(url_for('home'))

    tasks = load_tasks()
    tasks.append({
        "task": task_text,
        "completed": False,
        "due_date": due_date,
        "priority": priority,
        "start_writing": "",
        "elapsed_time": 0  # stored in milliseconds
    })
    save_tasks(tasks)
    return redirect(url_for('home'))

# Mark a task as completed
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = True
        save_tasks(tasks)
    return redirect(url_for('home'))

# Delete a task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(url_for('home'))

# Update the "start writing" field for a task
@app.route('/update_writing/<int:task_id>', methods=['POST'])
def update_writing(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        new_text = request.form.get('start_writing', '')
        tasks[task_id]['start_writing'] = new_text
        save_tasks(tasks)
    return redirect(url_for('home'))

# Update timer value for a task (AJAX route)
@app.route('/update_timer/<int:task_id>', methods=['POST'])
def update_timer(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        new_time = request.form.get('elapsed_time')
        if new_time is not None:
            try:
                tasks[task_id]['elapsed_time'] = int(new_time)
                save_tasks(tasks)
            except ValueError:
                pass
    return ('', 204)

# Reset timer for a task (AJAX route)
@app.route('/reset_timer/<int:task_id>', methods=['POST'])
def reset_timer(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]['elapsed_time'] = 0
        save_tasks(tasks)
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)

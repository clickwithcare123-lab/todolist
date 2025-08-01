from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
   
    def __repr__(self):
        return f'<Todo {self.title}>'

@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'medium')
    due_date_str = request.form.get('due_date', '')
   
    if not title:
        flash('Title is required!', 'error')
        return redirect(url_for('index'))
   
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format!', 'error')
            return redirect(url_for('index'))
   
    new_todo = Todo(
        title=title,
        description=description,
        priority=priority,
        due_date=due_date
    )
   
    db.session.add(new_todo)
    db.session.commit()
    flash('Todo added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    flash('Todo status updated!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
   
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date', '')
       
        if not title:
            flash('Title is required!', 'error')
            return render_template('edit.html', todo=todo)
       
        todo.title = title
        todo.description = description
        todo.priority = priority
       
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format!', 'error')
                return render_template('edit.html', todo=todo)
       
        todo.due_date = due_date
        db.session.commit()
        flash('Todo updated successfully!', 'success')
        return redirect(url_for('index'))
   
    return render_template('edit.html', todo=todo)

@app.route('/api/todos')
def api_todos():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([{
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'completed': todo.completed,
        'priority': todo.priority,
        'due_date': todo.due_date.isoformat() if todo.due_date else None,
        'created_at': todo.created_at.isoformat()
    } for todo in todos])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

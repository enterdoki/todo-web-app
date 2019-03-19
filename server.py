from flask import Flask, render_template, request, redirect, make_response, session, flash, Markup
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, TextField, validators, StringField, SubmitField, BooleanField
from string import Template
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship, backref
import requests
import os
import json


app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://enterdoki:1q2w3e4r5t@todo.clgjnattbiei.us-east-2.rds.amazonaws.com:3306/todo'
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(45), unique = True, nullable = False)
	todos = db.relationship('Todo', backref = 'user', lazy = True)
	
	def __init__(self, id, username):
			self.id = id
			self.username = username
        

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	todo = db.Column(db.String(45), nullable = False)
	completed = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
	
	def __init__(self, id, todo, user_id):
	        self.id = id
	        self.todo = todo
	        self.user_id = user_id;
	        self.completed = 0
	        
          

@app.route('/')
@app.route('/add', methods = ['POST'])
def welcome(): 	
	todos = []
	if 'username' in session:	
		current_user = User.query.filter_by(username = session['username']).first()
		if request.method == 'POST':
			new_todo = request.form['new_task']
			if new_todo != ' ':
				todo = Todo(None, new_todo, current_user.id)
				db.session.add(todo)
				db.session.commit()
		
		user_todos = Todo.query.filter_by(user_id = current_user.id).all()
		for todo in user_todos:
			todos.append([todo.id, todo.todo, todo.completed])

	
		return render_template('todo.html', todos = todos)
	else:
		return render_template('login.html')



@app.route('/login', methods = ['POST'])
def login():
	if request.method == 'POST':
		name = request.form['username']
		user = User.query.filter_by(username = name).first()
		if user:
			session['username'] = request.form['username']
			return redirect ('/')
		else:
			message = Markup("Username doesn't exist!")
			flash(message)
			return render_template('login.html')
		
	else:
		return render_template('login.html')	 


@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'POST':
		name = request.form['new_username']
		user = User.query.filter_by(username = name).first()
		if user:
			message = Markup("Username already exists!")
			flash(message)
			return render_template('register.html')

		new_user = User(None, name)	
		db.session.add(new_user)

		try:
			db.session.commit()
			message = Markup("Registered! Use it to log in now.")
			flash(message)
			return redirect('/')
		except Exception as error:
			db.session.rollback()
			raise
			
	else:
		return render_template('register.html')	


@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect('/')

@app.route('/delete/<task_name>')
def delete(task_name):
	if 'username' in session:
		todo = Todo.query.filter_by(id = task_name).first()
		db.session.delete(todo)
		db.session.commit()

	return redirect('/')

@app.route('/complete/<task_name>')
def complete(task_name):
	if 'username' in session:
		todo = Todo.query.filter_by(id = task_name).first()
		todo.completed = 1
		db.session.commit()

		return redirect('/')

@app.route('/uncomplete/<task_name>')
def uncomplete(task_name):
	if 'username' in session:
		todo = Todo.query.filter_by(id = task_name).first()
		todo.completed = 0
		db.session.commit()

		return redirect('/')


app.config['SECRET_KEY'] = os.urandom(12)
if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, threaded=True, debug = True)

from flask import Flask, render_template, request, redirect, make_response
from string import Template
import requests
import os
import json

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def welcome(): 
	if('sillyauth' in request.cookies):	
		r = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies = request.cookies)
		data = r.json()
		if (r.status_code == 200):
			return render_template('todo.html', todos = data)
	else:
		return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
   name = Template('{"username": "$name"}').safe_substitute(name = request.form['username'])
   r = requests.post('https://hunter-todo-api.herokuapp.com/auth', data = name)
   if (r.status_code == 200):
	   cookie = r.json()
	   resp = make_response(redirect('/'))
	   resp.set_cookie('sillyauth', cookie['token'])
	   return resp 
	
@app.route('/register', methods = ['POST', 'GET'])
def register():
	if request.method == 'POST':
		name = Template('{"username": "$name"}').safe_substitute(name = request.form['new_username'])
		requests.post('https://hunter-todo-api.herokuapp.com/user', data = name)
		return redirect('/')
	else:
		return render_template('register.html')	

@app.route('/logout')
def logout():
	resp = make_response(redirect('/'))
	resp.set_cookie('sillyauth', expires=0)
	return resp
	
@app.route('/add', methods=['POST'])
def add():
	if request.form['new_task']:
		task = Template('{"content": "$task" }').safe_substitute(task = request.form['new_task'])
		requests.post('https://hunter-todo-api.herokuapp.com/todo-item', data = task, cookies = request.cookies)
	return redirect('/')

@app.route('/delete/<task_name>')
def delete(task_name):
	requests.delete('https://hunter-todo-api.herokuapp.com/todo-item/' + task_name , cookies = request.cookies)
	return redirect('/')

@app.route('/done/<task_name>/<status>')
def done(task_name, status):
	if status == "true":
		r = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/' + task_name , data = '{"completed": true}', cookies = request.cookies)
		return redirect('/')
	if status == "false":
		r = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+ task_name , data = '{"completed": false}', cookies = request.cookies)
		return redirect('/')

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, threaded=True, debug = True)





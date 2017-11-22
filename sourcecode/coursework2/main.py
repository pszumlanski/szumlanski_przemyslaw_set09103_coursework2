import bcrypt
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, session, g

from flask import Flask
app = Flask(__name__)
users_location = 'static/sql/var/users.db'
offers_location = 'static/sql/var/offers.db'
app.secret_key = 'qdoih13b4jkbf'

def init_users_db():
    users_db = sqlite3.connect(users_location)
    users = users_db.cursor()
    with app.open_resource('static/sql/userschema.sql', mode='r') as f:
      users.executescript(f.read())
    users_db.commit()
    users_db.close()

def check_auth(email, password):
  users_db = sqlite3.connect(users_location)
  users = users_db.cursor()
  users.execute("SELECT * FROM users WHERE email = ?", (email,))
  user = users.fetchone()
  user_password = user[3]
  users_db.close()
  if password == user_password:
    return True
  else:
    return False

def get_user(email):
  users_db = sqlite3.connect(users_location)
  users = users_db.cursor()
  user = []
  users.execute("SELECT * FROM users WHERE email = ?", (email,))
  user = users.fetchone()
  users_db.close()
  if user == None:
    user = []
  return user

def init_offers_db():
  offers_db = sqlite3.connect(offers_location)
  offers = offers_db.cursor()
  with app.open_resource('static/sql/offerschema.sql', mode='r') as f:
    offers.executescript(f.read())
  offers_db.commit()
  offers_db.close()

def get_offers():
  offers_db = sqlite3.connect(offers_location)
  offers = offers_db.cursor()
  alloffers = []
  offers.execute('SELECT * FROM offers')
  for row in offers:
    alloffers.append(row)
  offers_db.close()
  if alloffers == None:
    alloffers = []
  return alloffers

@app.route('/logout/')
def logout():
  session['currentuser'] = []
  return redirect('/')

@app.route('/')
def root():
  alloffers = get_offers()
  loggedinuser = session['currentuser']
  return render_template('main.html', alloffers=alloffers,
    loggedinuser=loggedinuser), 200

@app.route("/signup/", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
      email = request.form['email']
      firstname = request.form['firstname']
      lastname = request.form['lastname']
      password = request.form['password']
      user_id = 1;
      users_db = sqlite3.connect(users_location)
      users = users_db.cursor()
      users.execute('insert into users values (?, ?, ?, ?, ?)',
        (email, firstname, lastname, password, user_id))
      users_db.commit()
      users_db.close()
      return redirect('/login')
    else:
      return render_template('signup.html'), 200

@app.route("/login/", methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    pw = request.form['password']
    loggedinuser = get_user(email)
    if check_auth(email, pw):
      session['currentuser'] = loggedinuser
      session['loggedin'] = True
      return redirect('/')
    else:
      return render_template('login.html'), 200
  else:
    return render_template('login.html'), 200

@app.route("/newoffer/", methods=['GET', 'POST'])
def newoffer():
  currentuser = session['currentuser']
  if request.method =='POST':
    title = request.form['title']
    location = request.form['location']
    salary = request.form['pay']
    contact = request.form['contact']
    desc = request.form['desc']
    user = session['currentuser']
    offers_db = sqlite3.connect(offers_location)
    offers = offers_db.cursor()
    offers.execute('insert into offers values (?, ?, ?, ?, ?, ?)',
      (title, location, salary, contact, desc, user[1]))
    offers_db.commit()
    offers_db.close()
    return redirect('/')
  else:
    return render_template('newoffer.html', currentuser=currentuser), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)


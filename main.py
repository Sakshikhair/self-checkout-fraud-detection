from flask import Flask, render_template, redirect, session, request
import mysql.connector
import os

app = Flask(__name__)
app.secret_key=os.urandom(24)

conn = mysql.connector.connect(host="Host_name", user="user", password="password", database="database")
cursor = conn.cursor()

@app.route("/")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/home")
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')

#TO LOGIN
@app.route("/login_validation", methods=['POST'])
def login_validation():
    lemail = request.form.get('login_email')
    lpassword = request.form.get('login_password')
    sql = "SELECT * from users WHERE email = %s AND password = %s"
    cursor.execute(sql, [lemail, lpassword])
    users = cursor.fetchall()
    print(users)

    if len(users)>0:
        session['user_id'] = users[0][0]
        return redirect('/home')
    else:
        return redirect('/')

#TO REGISTER
@app.route("/add_user", methods=['POST'])
def add_user():
    rname=request.form.get('register_name')
    remail=request.form.get('register_email')
    rpassword=request.form.get('register_password')
    sql = "INSERT INTO users(userid, name, email, password) VALUES (NULL, %s, %s, %s)"
    cursor.execute(sql, [rname, remail, rpassword])
    conn.commit()
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, [remail])
    myuser=cursor.fetchall()
    session['user_id']=myuser[0][0]
    return redirect('/home')

@app.route("/logout")
def logout():
    session.pop('user_id')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
import os
from flask import Flask, session,render_template,request,flash,redirect,url_for,g
from flask_session import Session
from sqlalchemy import create_engine
from functools import wraps
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from config.py import DATABASE_URL

app = Flask(__name__)

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'logged_in' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        return f(*args,**kwargs)

    return decorated_function

@app.route("/",methods=['GET','POST'])
def login():
    error=""
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=db.execute("SELECT * FROM users WHERE username=:username and password=:password",{"username":username,"password":password}).fetchone()

        if user is None or username!=user.username or password!=user.password:
            error="Invalid Login"
            return render_template("login.html",error=error)
        
        else:
            session['logged_in']=True
            session['user_id']=user.id
            return redirect(url_for('books'))
    return render_template("login.html",error=error)

@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in')
    flash('You are logged out')
    return redirect(url_for('login'))

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        error=""

        if username is None or password is None or email is None:
            print("error")
            error="Please fill all the fields"
        else:
            db.execute("INSERT INTO users (username,password,email) VALUES(:username,:password,:email)",{"username":username,"password":password,"email":email})
            db.commit()
            flash("Successfully Registered")
            return redirect(url_for("login"))
        
    return render_template('register.html')

@app.route("/books",methods=['GET'])
@login_required
def books():
    val=request.args.get('search')
    if val:
        books=db.execute("SELECT * FROM books WHERE isbn LIKE :isbn or title LIKE :title",{'isbn':val+"%",'title':val+"%"})
    else:
        books=db.execute("SELECT * FROM books LIMIT 12")
    return render_template('books.html',books=books)

    

if __name__=="__main__":
    app.run()
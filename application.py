import os
from flask import Flask, session,render_template,request,flash,redirect,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from functools import wraps
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import json
from datetime import datetime
from config import DATABASE_URL,BOOK_READ_API_KEY

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


@app.route("/books/<string:isbn>",methods=['GET','POST'])
@login_required
def book_detail(isbn):
    error=""
    user_id=session["user_id"]
    books=db.execute("SELECT * FROM books WHERE isbn=:isbn",{'isbn':isbn}).fetchone()
    book_id=books.id
    reviews=db.execute("SELECT * FROM reviews WHERE bookid=:bookid and userid=:userid",{"bookid":book_id,"userid":user_id})
    if request.method=='GET':
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": BOOK_READ_API_KEY, "isbns": isbn})
        return render_template('book_detail.html',response=res.json(),books=books)
    else:
        reviewtext=request.form['review']
        try:
            review_exist=db.execute("SELECT * FROM reviews WHERE userid=:userid and bookid=:bookid",{"userid":user_id,"bookid":book_id}).fetchone()
            if review_exist:
                error="You have already reviewed this book kappa!"
            else:
                print("INSERTING REVIEW FOR BOOK ID : {}, USER_ID : {}, REVIEW : {}, REVIEW_DATE : {}".format(book_id,user_id,reviewtext,datetime.now().date()))
                db.execute("INSERT INTO reviews (userid,bookid,review,review_date) VALUES(:user_id,:book_id,:review_text,:review_date)",{"user_id":user_id,"book_id":book_id,"review_text":reviewtext,"review_date":datetime.now().date()})
                print("INSERTED")
                db.commit()
                flash("REVIEW COMMITTED!")
        except:
            error="INSERT ERROR"
        return render_template('book_detail.html',error=error,books=books)

@app.route("/api/<string:isbn>")
@login_required
def book_api(isbn):
    books=db.execute("SELECT * FROM books WHERE isbn=:isbn",{'isbn':isbn}).fetchone()
    books_json={}
    books_json=books
    if books:
        return jsonify(books_json)
    else:
        return render_template('404.html')

if __name__=="__main__":
    app.run()
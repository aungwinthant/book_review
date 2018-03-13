from application import db
import csv

def main():
    create_tables()
    with open('books.csv') as f:
        reader=csv.reader(f)
        next(reader,None)
        for isbn,title,author,year in reader:
            print("adding book isbn = {}  title = {} author = {} year={}".format(isbn,title,author,year))
            db.execute("INSERT INTO books(isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":int(year)})
            print("added")
        db.commit()

def create_tables():
    print(".................CREATING TABLES.................................")
    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,username VARCHAR UNIQUE NOT NULL,password VARCHAR NOT NULL,email VARCHAR UNIQUE NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS books(id SERIAL PRIMARY KEY,isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year INTEGER)")
    db.execute("CREATE TABLE IF NOT EXISTS reviews(id SERIAL PRIMARY KEY, userid INTEGER REFERENCES users,bookid INTEGER REFERENCES books,review VARCHAR NOT NULL)")
    db.commit()
    print(".................TABLES ARE CREATED..............................")

if __name__=="__main__":
    main()
from application import db

class User(db.Model):

    __tablename__="users"

    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,nullable=False)
    email=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)

    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password

    def __str__(self):
        return '<name {0}>'.format(self.username)
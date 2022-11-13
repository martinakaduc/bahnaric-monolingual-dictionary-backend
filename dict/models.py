import json
from dict import db
from dict import bcrypt
from flask_login import UserMixin

user_word = db.Table('user_word',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('word_id', db.Integer, db.ForeignKey('word.id'))
                    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
        
    bookmark = db.relationship('Word', secondary=user_word, backref='bookmark_word', lazy='dynamic')
    
    def __repr__(self):
        return f'User {self.username}'
    
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def is_bookmarking(self, word):
        return self.bookmark.filter(user_word.c.word_id == word.id).count() > 0

    def edit_bookmark(self, word):
        if not self.is_bookmarking(word):
            self.bookmark.append(word) #if not bookmark, add 
            db.session.commit()
        else :
            self.bookmark.remove(word) #if bookmark, remove
            db.session.commit()               
    
    def bookmarked_word(self):
        return Word.query.join(
            user_word, (user_word.c.word_id==Word.id)
        ).filter(
            user_word.c.user_id == self.id
        ).order_by(
            Word.id.asc()
        )

    
class Word(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    pos = db.Column(db.String())
    BinhDinh = db.Column(db.String())
    KonTum = db.Column(db.String())
    GiaLai = db.Column(db.String())
    def to_dict(self):
        return {"name": self.name, "pos": self.pos, "BinhDinh": self.BinhDinh, "KonTum": self.KonTum, "GiaLai": self.GiaLai}
    
class DailyWord(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    word_id = db.Column(db.Integer(), db.ForeignKey('word.id'))
    date = db.Column(db.Date())

    daily = db.relationship('Word', backref='daily_word')

    def get_word_of_the_day(self):
        return Word.query.join(DailyWord, (self.word_id == Word.id)).first()


    


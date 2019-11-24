from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	posts = db.relationship('Post', backref='author', lazy=True)
	place = db.Column(db.String(20))
	type = db.Column(db.String(20), nullable=False)
	scor = db.Column(db.Integer, default=0)
	post_no = db.Column(db.Integer, default=0)
	post_acc = db.Column(db.Integer, default=0)
	post_compl = db.Column(db.Integer, default=0)
	doc_up = db.Column(db.Integer, default=0)
	docs = db.Column(db.String(20), nullable=True)
	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sum = db.Column(db.Integer, nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	interest = db.Column(db.Integer, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	payDate = db.Column(db.Date, nullable=False)
	description = db.Column(db.Text)
	def __repr__(self):
		return f"Post('{self.title}', '{self.date_posted}')"

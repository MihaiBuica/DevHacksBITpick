import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.forms import ClientInvestorButton
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

from flask import Flask
from flask import request, render_template, jsonify

import json

# type 0 = document updatat
# type 1 = plata completata
# type 2 = bani ceruti
# type 3 = postari totale
def calculate_score(type):
	if type == 0:
		calculated_value = 20
	elif type == 1:
		calculated_value = 10
	elif type == 2:
		calculated_value = 0
	elif type == 3:
		calculated_value = -5
		
	return calculated_value
	
def calculate_interest_sum(interest, sum):
	return sum*interest/100.0;
	

@app.route("/")
@app.route("/home")
def home():
	posts = Post.query.all()
	return render_template('home.html', posts=posts)


@app.route("/about")
def about():
	return render_template('about.html', title='About')


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    # You'd normally use the variables above to limit the data returned
    # you don't want to return ALL events like in this code
    # but since no db or any real storage is implemented I'm just
    # returning data from a text file that contains json elements

    with open("events.json", "r") as input_data:
        # you should use something else here than just plaintext
        # check out jsonfiy method or the built in json module
        return input_data.read()
	
@app.route("/register", methods=['GET', 'POST'])
def register():
	type = request.args['type']  # counterpart for url_for()
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password, type=type, place=form.place.data)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form, type=type)

	
@app.route("/prereg", methods=['GET', 'POST'])
def prereg():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = ClientInvestorButton()
	if form.validate_on_submit():
		if form.investor.data:
			return redirect(url_for('register', type='n Investor'))
		if form.client.data:
			return redirect(url_for('register', type=' Client'))
	return render_template('prereg.html', title='Registration', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check email and password', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.document = form.document.data
		val = 0
		if current_user.document:
			current_user.doc_up += 1
			val = calculate_score(0)
		current_user.scor += val
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account',
						   image_file=image_file, form=form)

def addJSON(title,desc,date):

	file = open('events.json', 'r')    
	content = file.read()	
	content = content[:-1]
	content_add = ",{\n\"title\":" + "\"" + title + "\"" + ",\n" + "\"desc\":" +"\"" + desc +"\"" + ",\n" + "\"start\":" +"\"" + date + "\"" +"\n" + "}]"    	
	content = content + content_add
	file = open('events.json', 'w')
	file.write(content)
	
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	if not current_user.scor:
		flash('Not enough points for a new demand')
		return redirect(url_for('home'))
	form = PostForm()
	if form.validate_on_submit():
		post = Post(sum=form.sum.data, payDate=form.payDate.data, author=current_user, interest=form.interest.data, description=form.description.data)		
		#addJSON(form.sum.data, form.interest.data, form.payDate.data)
		db.session.add(post)
		current_user.post_no += 1
		if current_user.scor is 0:
			flash('Your score is 0. We do not trust you. Change something in your life ;)', 'error')
			return redirect(url_for('home'))
		elif current_user.post_no is 4:
			flash('Your have more than 3 posts. Cataua achita datoriiaaa', 'error')
			return redirect(url_for('home'))
		else:
			val = calculate_score(3)
			current_user.scor += val
			db.session.commit()
			flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post',
						   form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.sum, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	lat, lng = 0,0
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post',
						   form=form, legend='Update Post', Lat = lat, Lng = lng)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Payment has been transfered!', 'success')
	return redirect(url_for('home'))

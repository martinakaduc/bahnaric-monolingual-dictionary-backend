
from dict import app
from flask import render_template, redirect, url_for, flash, request
from dict.models import Word, User, user_word
from dict.forms import RegisterForm, LoginForm, SearchForm, BookmarkForm
from flask_paginate import Pagination, get_page_parameter
from dict import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route("/dict", methods=["GET","POST"])
@login_required
def dict_page():
    bookmark_form = BookmarkForm()
    if request.method == "POST":
        bookmarked_word = request.form.get('bookmarked_word')
        word_obj = Word.query.filter_by(name = bookmarked_word).first()
        current_user.add_bookmark(word_obj)
        return redirect(url_for("dict_page"))
        
    if request.method == "GET":
        page = request.args.get('page', 1, type = int)
        words = Word.query.paginate(page, per_page=20)
        return render_template("dict.html", words = words, bookmark_form=bookmark_form)

@app.route("/register", methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created !! You are now logged in as {user_to_create.username}", category="success")
        return redirect(url_for('dict_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success!!! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('dict_page'))
        else:
            flash('Username or password is not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout_page():
    logout_user()
    flash("Logged out successfully!!!", category="info")
    return redirect(url_for("home_page"))
    
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)   
    
@app.route('/search', methods=['POST'])
def search_page():
    form = SearchForm()
    words = Word.query
    if form.validate_on_submit():
        page = request.args.get('page', 1, type = int)
        searched_word = form.searched.data
        words = words.filter(Word.name.like('%' + searched_word + '%'))
        
        words = words.order_by(Word.id).all()
        return render_template('search.html', form=form, 
                               searched =searched_word
                               ,words = words)
        
@app.route('/bookmark', methods=['GET', 'POST'])
@login_required
def bookmark_page():
    words = current_user.bookmarked_word()
    return render_template('bookmark.html', words = words)

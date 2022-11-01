
from datetime import datetime
import random
from dict import app, db, bana_bd, bana_gl, bana_kt, os
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from dict.models import Word, User, user_word, DailyWord
from dict.forms import RegisterForm, LoginForm, SearchForm, BookmarkForm
from flask_paginate import get_page_parameter
from flask_sqlalchemy import Pagination
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')

@app.route("/api/dict", methods=["GET"])
# @login_required
def dict_page():
    word_per_page = 20
    page = request.args.get('page', 1, type = int)
    words = Word.query.paginate(page = page, per_page = word_per_page)
    words_dict = [word.to_dict() for word in words.items]
    return jsonify({"next": f'http://localhost:5000/api/dict?page={words.next_num}', "previous": f'http://localhost:5000/api/dict?page={words.prev_num}',"results": words_dict})
    # return render_template("dict.html",
    #                         words = words,
    #                         c_user = current_user)

@app.route("/update", methods=["POST"])
def update():
    word_obj = Word.query.filter_by(id = request.form['id']).first()
    current_user.edit_bookmark(word_obj)
    return jsonify({'result' : 'success'})

@app.route('/api/search', methods=['POST','GET'])
def search_page():
    form = SearchForm()
    words = Word.query
    word_per_page = 20
    if form.validate_on_submit():
        searched_word = form.searched.data
        words = words.filter(Word.name.like('%' + searched_word + '%'))
        words = words.order_by(Word.id).all()
        words_dict = [word.to_dict() for word in words]
    # if request.method == "GET":
    #     page = request.args.get('page', 1, type = int)
    #     start = (page - 1) * word_per_page
    #     end = start + word_per_page
    #     items = words[start:end]
    #     words = Pagination(None, page, word_per_page, len(items), items)

        return jsonify({"results": words_dict})
        # return render_template('search.html',
        #                        words = words,
        #                        c_user = current_user)
    # flash(f"Type nothing bro ?", category="danger")
    # return redirect(url_for('dict_page'))
        
@app.route('/bookmark', methods=['GET', 'POST'])
# @login_required
def bookmark_page():
    word_per_page = 20
    words = current_user.bookmarked_word()
    page = request.args.get('page', 1, type = int)
    words = words.paginate(page = page, per_page = word_per_page)
    return render_template("bookmark.html",
                            words = words,
                            c_user = current_user)

@app.route("/daily", methods=["GET", "POST"])
# @login_required
def daily_page():
    daily_word = DailyWord.query.order_by(DailyWord.id.desc()).first()

    if (not daily_word) or daily_word.date < datetime.now().date():
        ran_num =  random.randrange(Word.query.first().id, Word.query.count())

        daily_word = DailyWord(word_id=ran_num,
                                date=datetime.now()
                                )
        db.session.add(daily_word)
        db.session.commit()

    # join DailyWord and Word relation and get word
    word_of_the_day = daily_word.get_word_of_the_day()

    return render_template("daily.html",
                            word = word_of_the_day,
                            c_user = current_user)

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


@app.route('/<region_tag>/<word>', methods=['GET'])
def download(region_tag, word):
    dir = ""
    fn = ""

    if region_tag == "BD":
        dir = os.path.join(bana_bd, word)

    elif region_tag == "KT":
        dir = os.path.join(bana_kt, word)

    elif region_tag == "GL":
        dir = os.path.join(bana_gl, word)   
    else:
        return abort(404)
    dir = dir.strip()
    try:
        list_files = os.listdir(dir)
    except:
        return abort(404)
    fn = random.choice(list_files)

    return send_from_directory(directory=dir, path=fn)

    


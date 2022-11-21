import datetime
from datetime import datetime, timezone, timedelta
import random
import json
from dict import app, db, bana_bd, bana_gl, bana_kt, os
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from dict.models import Word, User, user_word, DailyWord
from dict.forms import RegisterForm, LoginForm, SearchForm, BookmarkForm
from flask_paginate import get_page_parameter
from flask_sqlalchemy import Pagination
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, unset_jwt_cookies, jwt_required, current_user, JWTManager

@app.after_request 
def refresh_expiring_jwts(response): #used to refresh token :D just ignore this part :D
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes = 15))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

#send POST to this url, JSON format 
# {
#     "username": ???,
#     "password": ???
# }
@app.route('/api/login', methods=["POST"])
def create_token():                                         
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    attempted_user = User.query.filter_by(username=username).one_or_none()
    if attempted_user and attempted_user.check_password_correction(attempted_password=password):
        access_token = create_access_token(identity=attempted_user) #create token
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Invalid username or password"}), 401   

@app.route("/api/logout", methods=["POST"])
def logout():  #not complete yet
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

#send GET, remember to include in request's Header: Authorization: Bearer <token>
@app.route('/api/bookmark', methods=["GET"])
@jwt_required() #protected page
def api_bookmark():
    
    word_per_page = 20
    words = current_user.bookmarked_word()
    page = request.args.get('page', 1, type = int)
    words = words.paginate(page = page, per_page = word_per_page)
    words_dict = [word.to_dict() for word in words.items]
    
    next_link = None if words.next_num == None else f'http://localhost:5000/profile?page={words.next_num}'
    prev_link = None if words.prev_num == None else f'http://localhost:5000/profile?page={words.prev_num}'

    return jsonify({"next": next_link, "previous": prev_link,"results": words_dict})

#send POST to this url, json format 
# {
#     "username": ???,
#     "email_address": ???,
#     "password1": ???,
#     "password2": ???
# }
@app.route("/api/register", methods=['POST'])
def api_register():
    form = RegisterForm()
    form.username.data = request.json.get("username", None)
    form.email_address.data = request.json.get("email_address", None)
    form.password1.data = request.json.get("password1", None)
    form.password2.data = request.json.get("password2", None)   #inject data to form
    
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return jsonify({"msg": "create success !!!!!"})  
    if form.errors != {}:
        output = []
        for err_msg in form.errors.values():
            user_err = {}
            user_err['msg'] = f'There was an error: {err_msg}'
            output.append(user_err)
        return jsonify({'err': output})
    return jsonify({"msg": "create success ?"})        

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

    next_link = None if words.next_num == None else f'http://localhost:5000/api/dict?page={words.next_num}'
    prev_link = None if words.prev_num == None else f'http://localhost:5000/api/dict?page={words.prev_num}'

    return jsonify({"next": next_link, "previous": prev_link,"results": words_dict})

@app.route("/update", methods=["POST"])
def update():
    word_obj = Word.query.filter_by(id = request.form['id']).first()
    current_user.edit_bookmark(word_obj)
    return jsonify({'result' : 'success'})

@app.route('/api/search', methods=['GET'])
def search_page():
    word_per_page = 20
    page = request.args.get('page', 1, type = int)
    searched_word = request.args.get('searched_word','', type=None)
    if searched_word == '':
        return abort(400)
    words = Word.query.filter(Word.name.like('%' + searched_word + '%'))
    words = words.order_by(Word.id).paginate(page = page, per_page = word_per_page)
    words_dict = [word.to_dict() for word in words.items]

    next_link = None if words.next_num == None else f'http://localhost:5000/api/search?searched_word={searched_word}&page={words.next_num}'
    prev_link = None if words.prev_num == None else f'http://localhost:5000/api/search?searched_word={searched_word}&page={words.prev_num}'
    
    return jsonify({"next": next_link, "previous": prev_link,"results": words_dict})
        
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

@app.route("/api/daily", methods=["GET"])
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
    word_of_the_day = daily_word.get_word_of_the_day().to_dict()

    return jsonify({"results": word_of_the_day})

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

    


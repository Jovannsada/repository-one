import os

from flask import Flask, render_template, url_for, redirect, session, flash, g, request, abort
from flask_mail import Message
from flask_mail import Mail

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,  current_user
from threading import Thread

app = Flask(__name__)

from database_users import Base, Users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine('sqlite:///Users.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession
app.config['SECRET_KEY'] = 'deVElpPasswordkey1!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
mail = Mail(app)
set_FLASKY_ADMIN='ed25ntende'
set_MAIL_USERNAME ='Gmail username'
set_MAIL_PASSWORD ='Gmail password'

bootstrap = Bootstrap
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template = '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    # mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class LoginForm(FlaskForm):
    Username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    Password = PasswordField('Enter your password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    Full_names = StringField('Full Name', validators=[InputRequired(), Length(min=7, max=50)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    Password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
    submit = SubmitField('Sign Up')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    #to check whether the form was submitted on the page
    if form.validate_on_submit():
        user = Users.query.filter_by(Username=form.Username.data).first()
        if user:
            if check_password_hash(user.Password, form.password.data):
                load_user(user.password, remember=form.remember.data)
                return redirect(url_for('fresh_tomatoes.html'))
        return '<h1>Invalid Username or password</h1>'

                # session['Username'] = form.Username.data
    return render_template('login.html', form=form)

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    #to check whether the form has been submitted
    if form.validate_on_submit():
        user = session.query.filter_by(Username=form.Username.data).first()
        if user is None:
            user = Users(Username=form.Username.data)
            session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.Username.data
        form.Username.data=''
        hashed_password = generate_password_hash(form.Password.data, method='sha256')
        new_user = Users(Full_names=form.Full_names.data, username=form.username.data, email=form.email.data, Password=hashed_password)
        session.add(new_user)
        session.commit()
        return redirect(url_for('fresh_tomatoes.html'))
         # return '<h1>New user has been added</h1>'
        # return '<h1>' + form.Username.data + '' + form.email.data + '' + form.password.data + '</h1>'
        # return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/fresh_tomatoes')
@login_required
def alienmoviecatalogue():
    return render_template('fresh_tomatoes.html', name=current_user.Username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__=='__main__':
    app.run(debug=True)
# from passlib.hash import sha256_crypt
from functools import wraps

import mysql.connector
from flask import (Flask, render_template, flash, redirect, url_for, session, request,
    # logging
                   )
from wtforms import Form, StringField, PasswordField, validators, TextAreaField


def main():
    app = Flask(__name__)
    app.debug = False

    def make_connection():
        config = {
            'user': 'root',
            'password': 'root',
            'host': 'db',
            'port': '3306',
            'database': 'flaskapp',
            # 'auth_plugin': 'mysql_native_password'
        }
        return mysql.connector.connect(**config)

    connection = make_connection()

    # Articles = Articles()

    @app.route('/')
    def index():
        return render_template('home.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/articles')
    def articles():

        # create cursor
        cur = connection.cursor()

        # get articles
        cur.execute("SELECT * FROM articles")
        _articles = cur.fetchall()

        if _articles:
            return render_template('articles.html', articles=_articles)
        else:
            msg = 'No Articles Found'
            return render_template('articles.html', msg=msg)

    @app.route('/article/<string:id_str>/')
    def article(id_str):
        # create cursor
        cur = connection.cursor()

        # get article
        cur.execute("SELECT * FROM articles WHERE id = %s", [id_str])
        _article = cur.fetchone()

        return render_template('article.html', article=_article)

    class RegisterForm(Form):
        name = StringField('Name', [validators.Length(min=1, max=50)])
        username = StringField('Username', [validators.Length(min=4, max=25)])
        email = StringField('Email', [validators.Length(min=4, max=25)])
        password = PasswordField('Password',
                                 [validators.DataRequired(),
                                  validators.EqualTo('confirm',
                                  message='passwords do not match')])
        confirm = PasswordField('Confirm password')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            # TODO: REMOVE ENCRYPTION IN PASSWORD
            password = form.password.data
            # password = sha256_crypt.encrypt(str(form.password.data))

            # Create cursor
            cur = connection.cursor()

            cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",
                        (name, email, username, password))

            # commit to DB
            connection.commit()
            # close connection
            cur.close()

            flash("You are now Registered and you can login", 'success')

            redirect(url_for('login'))
        return render_template('register.html', form=form)

    # user login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Get Form Fields
            username = request.form['username']
            password_candidate = request.form['password']

            # Create cursor

            cur = connection.cursor()

            # Get user by username

            cur.execute("SELECT * FROM users WHERE username = %s", [username])
            data = cur.fetchone()

            if data:
                # Get Stored hash
                # data = cur.fetchone()
                password = data[-1]

                # Compare Passwords
                # if sha256_crypt.verify(password_candidate, password):
                if password_candidate == password:
                    # Passed
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in ', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Username not found'
                    return render_template('login.html', error=error)

            else:
                error = 'Username not found'
                return render_template('login.html', error=error)

        return render_template('login.html')

    # check if user logged in
    def is_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('Unauthorized, please login', 'danger')
                return redirect(url_for('login'))
        return wrap

    # logout
    @app.route('/logout')
    @is_logged_in
    def logout():
        session.clear()
        flash('you are now logged out ', 'success')
        return redirect(url_for('login'))

    # Dashboard
    @app.route('/dashboard')
    @is_logged_in
    def dashboard():

        # create cursor
        cur = connection.cursor()

        # get articles
        cur.execute("SELECT * FROM articles")
        _articles = cur.fetchall()

        if _articles:
            return render_template('dashboard.html', articles=_articles)
        else:
            msg = 'No Articles Found'
            return render_template('dashboard.html', msg=msg)

    # Article form class

    class ArticleForm(Form):
        title = StringField('Title', [validators.Length(min=1, max=50)])
        body = TextAreaField('Body', [validators.Length(min=30, max=1000)])

    # Add Article
    @app.route('/add_article', methods=['GET', 'POST'])
    @is_logged_in
    def add_article():
        form = ArticleForm(request.form)
        if request.method == 'POST' and form.validate():
            title = form.title.data
            body = form.body.data

            # Create a cursor
            cur = connection.cursor()

            # execute
            cur.execute("INSERT INTO articles(title,body,author) VALUES(%s, %s, %s)",
                        (title, body, session['username']))

            # commit to db
            connection.commit()

            # close connection
            cur.close()

            flash('Article created ', 'success')

            return redirect(url_for('dashboard'))

        return render_template('add_article.html', form=form)

    # Edit Article
    @app.route('/edit_article/<string:id_str>', methods=['GET', 'POST'])
    @is_logged_in
    def edit_article(id_str):
        # Create cursor
        cur = connection.cursor()
        # get article by id
        cur.execute("SELECT * FROM articles WHERE id = %s", [id_str])
        _article = cur.fetchone()

        # get form
        form = ArticleForm(request.form)

        # populate article form fields
        form.title.data = _article['title']
        form.body. data = _article['body']

        if request.method == 'POST' and form.validate():
            title = request.form['title']
            body = request.form['body']

            # Create a cursor
            cur = connection.cursor()

            # execute
            cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s",
                        (title, body, id))

            # commit to db
            connection.commit()

            # close connection
            cur.close()

            flash('Article Updated ', 'success')

            return redirect(url_for('dashboard'))

        return render_template('edit_article.html', form=form)

    # Delete article
    @app.route('/delete_article/<string:id_str>', methods=['POST'])
    @is_logged_in
    def delete_article(id_str):
        # Create cursor
        cur = connection.cursor()

        # Execute
        cur.execute("DELETE FROM articles WHERE id = %s", [id_str])

        # Commit to DB
        connection.commit()

        # close connection
        cur.close()

        flash('Article Deleted  ', 'success')

        return redirect(url_for('dashboard'))

    return app


if __name__ == "__main__":
    app = main()
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0')

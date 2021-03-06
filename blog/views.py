# -*- coding: utf-8 -*-
from flask import render_template, request, url_for, redirect, flash, session, make_response
from flask_login import login_user, login_required, logout_user, current_user

from blog import app, db, cache
from blog.models import User, Article

from captcha.image import ImageCaptcha
from random import randint
import re

@app.route('/', methods=['GET', 'POST'])
@cache.cached()
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        date = request.form['date']
        text = request.form['text']

        if not title or not re.fullmatch("[0-9]{2}-[0-9]{2}-[0-9]{2}", date) or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        article = Article(title=title, date=date, text=text)
        db.session.add(article)
        db.session.commit()
        flash('Item created.')
        cache.delete(key='view//')
        return redirect(url_for('index'))

    articles = Article.query.all()
    return render_template('index.html', articles=articles)


@app.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
#@login_required
def edit(article_id):
    article = Article.query.get_or_404(article_id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        date = request.form['date']
        text = request.form['text']

        if not title or not re.fullmatch("[0-9]{2}-[0-9]{2}-[0-9]{2}", date) or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', article_id=article_id))

        article.title = title
        article.date = date
        article.text = text
        db.session.commit()
        flash('Item updated.')
        cache.delete(key='view//')
        return redirect(url_for('index'))

    return render_template('edit.html', article=article)


@app.route('/article/delete/<int:article_id>', methods=['POST'])
@login_required
def delete(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Item deleted.')
    cache.delete(key='view//')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        cache.delete(key='view//')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        code = request.form['code']

        if not username or not password or not code:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password) and session.get('code') == code:
            login_user(user)
            flash('Login success.')
            cache.delete(key='view//')
            return redirect(url_for('index'))

        flash('Invalid username, password or validation code.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    cache.delete(key='view//')
    return redirect(url_for('index'))

@app.route('/captcha')
#@login_required
def return_captcha():
    code = '%04x' % randint(0, 0xffff)
    cap = ImageCaptcha().generate(code)
    cap = cap.getvalue()
    response = make_response(cap)
    response.headers['Content-Type'] = 'image/gif'
    session['code'] = code
    return response

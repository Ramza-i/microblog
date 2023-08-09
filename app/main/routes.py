import os.path
from datetime import datetime
from app import db
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.main.forms import EditProfileForm, PostForm, EmptyForm
from app.models import User, Post

from app.main import bp

@bp.before_request
def before():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)           # Получаем из GET-запроса значение по ключу page, если его в запросе нет - 1. Параметры в запрос можем пихать сами через &
    posts = current_user.followed_posts().paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Пост отправлен!')
        return redirect(url_for('main.index'))

    return render_template('index.html', title='Главная', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Все посты', posts=posts.items, next_url=next_url, prev_url=prev_url)



@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    userlist = User.query.all()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, title=f'Home|{username}', userlist=userlist, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.avatar.data:
            file = form.avatar.data
            filename = f"{current_user.username}.{secure_filename(file.filename).split('.')[-1]}"
            file.save(os.path.join('app', 'static', 'imgs', 'userimg', filename))
            current_user.avatar = filename
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('main.user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title=f'{current_user.username}|Редактирование')


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'Вы подписаны на {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'Вы отписались от {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))



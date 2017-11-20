from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Dog, Post


@api.route('/dogs/<int:id>')
def get_dog(id):
    dog = Dog.query.get_or_404(id)
    return jsonify(dog.to_json())


@api.route('/dogs/<int:id>/posts/')
def get_dog_posts(id):
    dog = Dog.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = dog.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_dog_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_dog_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/dogs/<int:id>/timeline/')
def get_dog_followed_posts(id):
    dog = Dog.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = dog.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', page=page+1,
                       _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

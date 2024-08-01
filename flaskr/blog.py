from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import User, Post, db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts_stmt = (
        db.select(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username
        )
        .join(User, Post.author_id == User.id)
        .order_by(Post.created.desc())
    )
    posts = db.session.execute(posts_stmt).fetchall()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is the author.

    :param id: id of post to get
    :param check_author: require the current user to be thye author
    :return: the post with author information
    :raise 404: if a post with the given id doen't exist
    :raise 403: if the current user isn't the author
    """
    post_stmt = (
        db.select(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username
        )
        .join(User, Post.author_id == User.id)
        .where(Post.id == id)
    )
    post = db.session.execute(post_stmt).one_or_none()
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db.session.execute(
                db.insert(Post),
                [{"title": title, "body": body, "author_id": g.user.id}],
            )
            db.session.commit()
            return redirect(url_for("blog.index"))
    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db.session.execute(
                db.update(Post).where(Post.id == id).values(title=title, body=body)
            )
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("/blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the author of the post.
    """
    get_post(id)
    db.session.execute(db.delete(Post).where(Post.id == id))
    db.session.commit()
    return redirect(url_for("blog.index"))

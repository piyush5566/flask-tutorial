import os
import typing as t
from flask import Flask, abort, current_app, render_template_string
from flask_babel import Babel
from flask_security import (
    Security,
    current_user,
    auth_required,
    hash_password,
    SQLAlchemyUserDatastore,
    permissions_accepted,
    roles_accepted,
)
from flask_mailman import Mail
from .models import User, Role, Post
from .db import db


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "lf1Z52RiiEDSFyBe3upInChoOM_pSvIjHQF8qB9Y-90"
    app.config["SECURITY_PASSWORD_HASH"] = "argon2"
    # argon2 uses double hashing by default - so provide key.
    app.config["SECURITY_PASSWORD_SALT"] = "13963925385433668630863375132877810881"

    # Take password complexity seriously
    app.config["SECURITY_PASSWORD_COMPLEXITY_CHECKER"] = "zxcvbn"

    # Allow registration of new users without confirmation
    app.config["SECURITY_REGISTERABLE"] = True

    app.config["SECURITY_RECOVERABLE"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///flaskr.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    # As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the
    # underlying engine. This option makes sure that DB connections from the pool
    # are still valid. Important for entire application since many DBaaS options
    # automatically close idle connections.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}
    app.config["MAIL_BACKEND"] = "file"
    app.config["MAIL_FILE_PATH"] = (
        r"C:\Users\pgh55\Documents\Learn\WebDev\flask-tutorial\flaskr\app-messages"
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    # Setup Babel - not strictly necessary but since our virtualenv has Flask-Babel
    # we need to initialize it
    Babel(app)

    # Set this so unit tests can mock out
    app.post_cls = Post

    mail = Mail(app)
    mail.init_app(app)

    # apply the blueprints to the app

    @app.route("/admin")
    @auth_required()
    @permissions_accepted("admin-read", "admin-write")
    def admin():
        return render_template_string(
            f"Hello on admin page. Current user {current_user.email} password is {current_user.password}"
        )

    @app.route("/ops")
    @auth_required()
    @roles_accepted("monitor")
    def monitor():
        return render_template_string("Hello OPS")

    from . import blog

    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint="index")

    return app


# Create users and roles (and first post!)
def create_users():
    if current_app.testing:
        return
    with current_app.app_context():
        security = current_app.security
        security.datastore.db.create_all()
        security.datastore.find_or_create_role(
            name="admin",
            permissions={"admin-read", "admin-write", "user-read", "user-write"},
        )
        security.datastore.find_or_create_role(
            name="monitor", permissions={"admin-read", "user-read"}
        )
        security.datastore.find_or_create_role(
            name="user", permissions={"user-read", "user-write"}
        )
        security.datastore.find_or_create_role(name="reader", permissions={"user-read"})

        if not security.datastore.find_user(email="ops@me.com"):
            security.datastore.create_user(
                email="ops@me.com",
                password=hash_password("password"),
                username="ops",
                roles=["monitor"],
            )
        real_user = security.datastore.find_user(email="user@me.com")
        if not real_user:
            real_user = security.datastore.create_user(
                email="user@me.com", password=hash_password("password"), roles=["user"]
            )
        if not security.datastore.find_user(email="reader@me.com"):
            security.datastore.create_user(
                email="reader@me.com",
                password=hash_password("password"),
                username="reader",
                roles=["reader"],
            )

        post = current_app.post_cls(
            title="First Post", body="My first post is short.", user=real_user
        )
        security.datastore.db.session.add(post)
        security.datastore.db.session.commit()


app = create_app()
with app.app_context():
    create_users()

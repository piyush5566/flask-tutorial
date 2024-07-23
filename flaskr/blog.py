from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werzeug.exceptions import abort
from flaskr.auth import login_required
from flakr.db import get_db

bp = Blueprint('blog', __name__)

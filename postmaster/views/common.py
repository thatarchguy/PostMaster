"""
Author: StackFocus
File: common.py
Purpose: UI routes for the app
"""

from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from jinja2 import evalcontextfilter, Markup, escape
from postmaster import app, forms, models, login_manager
from postmaster.utils import get_wtforms_errors
from postmaster.utils import json_logger

common = Blueprint('common', __name__)


@app.template_filter()
@evalcontextfilter
def new_line_to_break(eval_ctx, value):
    """ Jinja2 filter to convert all \n to <br> while escaping the text
    """
    result = ''
    for i, line in enumerate(value.split('\n')):
        if i != 0:
            result += '<br>'
        result += str(escape(line))

    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@login_manager.user_loader
def user_loader(user_id):
    """ Function to return user for login
    """
    return models.Admins.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    """ Function to redirect after logging in when prompted for login
    """
    return redirect('/login?next=' + request.path)


@app.route('/', methods=['GET'])
@login_required
def index():
    """ Function to return index page
    """

    return render_template('index.html', title='PostMaster Dashboard',
                           authenticated=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ This is the login route and processing of information
    """
    # Calls the new function in order to refresh the auth_source list
    login_form = forms.LoginForm.new()

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        if request.method == 'GET':
            return render_template('login.html', title='PostMaster Login', loginForm=login_form)
        elif login_form.validate_on_submit():
            login_user(login_form.admin, remember=False)
            json_logger(
                'auth', login_form.admin.username,
                'The administrator "{0}" logged in successfully'.format(
                    login_form.admin.username))
            return redirect(request.args.get('next') or url_for(
                'index'))
        else:
            wtforms_errors = get_wtforms_errors(login_form)
            if wtforms_errors:
                flash(wtforms_errors)

    return redirect(url_for('login'))


@app.route('/logout', methods=["GET"])
def logout():
    """
    Logs current user out
    """
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully logged out', 'success')

    return redirect(url_for('login'))


@app.route('/domains', methods=["GET"])
@login_required
def domains():
    """
    Manages domains in the database
    """

    return render_template('domains.html', title='PostMaster Domains',
                           authenticated=current_user.is_authenticated)


@app.route('/users', methods=["GET"])
@login_required
def users():
    """
    Manages users/email accounts in the database
    """

    return render_template('users.html', title='PostMaster Users',
                           authenticated=current_user.is_authenticated)


@app.route('/aliases', methods=["GET"])
@login_required
def aliases():
    """
    Manages aliases in the database
    """

    return render_template('aliases.html', title='PostMaster Aliases',
                           authenticated=current_user.is_authenticated)


@app.route('/admins', methods=["GET"])
@login_required
def admins():
    """
    Manages admins in the database
    """

    return render_template('admins.html', title='PostMaster Administrators',
                           authenticated=current_user.is_authenticated)


@app.route('/configs', methods=["GET"])
@login_required
def configs():
    """
    Manages configs in the database
    """

    return render_template('configs.html', title='PostMaster Configurations',
                           authenticated=current_user.is_authenticated)


@app.route('/logs', methods=["GET"])
@login_required
def logs():
    """
    Displays logs from the log file
    """

    return render_template('logs.html', title='PostMaster Logs',
                           authenticated=current_user.is_authenticated)

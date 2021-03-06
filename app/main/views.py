from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, session
#from flask.ext.login import login_user, logout_user, login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import VEditForm
#from ..decorators import admin_required, permission_required
from werkzeug import secure_filename
import os,time,datetime,copy,math


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

@main.route('/', methods=['GET', 'POST'])
def index():
    form = VEditForm()
    return render_template('index.html',form=form)


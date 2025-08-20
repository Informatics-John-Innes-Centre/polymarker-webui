import logging
import os
import sys

from flask import Flask, jsonify
from flask_mail import Mail

from pmwui.polymarker import run_pm
from pmwui.scheduler import Scheduler

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)


def create_app(test_config=None):
    log.info('creating pmwui flask app')

    app = Flask(__name__, instance_relative_config=True)

    app.logger.handlers = log.handlers
    app.logger.setLevel(log.level)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_HOST='localhost',
        DATABASE_USER='polymarker',
        DATABASE_PASSWORD='',
        DATABASE_NAME='polymarker_webui_dev',
        UPLOAD_DIR=os.path.join(app.instance_path, 'uploads'),
        RESULTS_DIR=os.path.join(app.instance_path, 'results'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)
    os.makedirs(app.config['RESULTS_DIR'], exist_ok=True)

    app.mail = Mail(app)

    @app.route('/ver')
    def version():
        import importlib.metadata
        ver = importlib.metadata.version('pmwui')
        return jsonify({'version': ver})

    from . import db
    db.init_app(app)

    from . import api
    app.register_blueprint(api.bp)

    from . import base
    app.register_blueprint(base.bp)
    app.add_url_rule('/', endpoint='index')

    app.scheduler = Scheduler(app.config, app, run_pm)

    # hack to prevent the scheduler running for utility commands
    if not ('init' in sys.argv or 'import' in sys.argv or 'gc' in sys.argv):
        app.scheduler.start()

    return app

import datetime
import logging
import os.path
import uuid

import markdown
from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, abort
from werkzeug.utils import redirect

from pmwui.db import db_get

bp = Blueprint('base', __name__)

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)


def get_references():
    log.debug("fetching reference genomes")
    db = db_get()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, display_name, description, example FROM reference")
    references = cursor.fetchall()

    ref_list = []

    for r in references:
        ref_list.append(r + (markdown.markdown(r[3]),))

    log.debug(f"found {len(ref_list)} reference genomes")

    return ref_list


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':

        log.debug("POST request, submitting job to scheduler")

        manual_input = request.form['manual_input']
        query_file = request.files['query_file']
        reference = request.form['reference']
        email = request.form['email']

        if query_file.filename == '' and manual_input == '':
            flash('No input provided.')
            return render_template('base/index.html', references=get_references())

        job_id = uuid.uuid4()

        if query_file.filename != '':
            query_file.save(os.path.join(current_app.config['UPLOAD_DIR'], f"{job_id}.csv"))
        else:
            file = open(os.path.join(current_app.config['UPLOAD_DIR'], f"{job_id}.csv"), 'w')
            file.write(manual_input)
            file.close()

        db_query = """
        INSERT INTO query (uid, reference, email, date)
        VALUES (?, ?, ?, ?)
        """

        db = db_get()
        cursor = db.cursor()
        cursor.execute(db_query, (job_id, reference, email, datetime.datetime.now()))
        db.commit()

        current_app.scheduler.submit(job_id)
        current_app.scheduler.poke()

        return redirect(f"/results/{job_id}")

    return render_template('base/index.html', references=get_references())


@bp.route('/uploads/<job_id>')
def download_file(job_id):
    return send_from_directory(current_app.config["UPLOAD_DIR"], job_id + '.csv')


@bp.route('/results/<job_id>/<filename>')
def result_file(job_id, filename):
    return send_from_directory(os.path.join(current_app.config["RESULTS_DIR"], job_id) + '_out', filename)


@bp.route('/cite')
def cite():
    return render_template('base/cite.html')


@bp.route('/designed_primers')
def designed_primers():
    return render_template('base/designed_primers.html')


@bp.route('/about')
def about():
    return render_template('base/about.html', references=get_references())


@bp.route('/results/<job_id>')
def result(job_id):
    db = db_get()
    cursor = db.cursor()
    cursor.execute("SELECT reference, email FROM query WHERE uid = %s", (job_id,))
    reference = cursor.fetchone()

    if reference is None:
        abort(404)

    status = "init"
    try:
        with open(f"{current_app.config['RESULTS_DIR']}/{job_id}_out/status.txt", 'r') as f:
            lines = f.read().splitlines()
            status = lines[-1]
    except FileNotFoundError:
        log.warning("status file not ready")

    return render_template('base/results.html', job_id=job_id, status=status,
                           queue_len=current_app.scheduler.get_queue_len())

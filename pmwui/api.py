import datetime
import logging
import os
import uuid

from flask import (Blueprint, jsonify, request, current_app)

from pmwui.db import db_get

bp = Blueprint('api', __name__, url_prefix='/api')

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)


@bp.route('/references', methods=('GET',))
def api_references():
    db = db_get()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM reference')
    ref_name_rows = cursor.fetchall()

    ref_names = [name[0] for name in ref_name_rows]

    return jsonify({"references": ref_names})


@bp.route('/submit', methods=('POST',))
def api_submit():
    log.debug("API POST request, submitting job to scheduler")

    job_id = uuid.uuid4()
    job_data = request.get_json()
    job_reference = job_data["reference"]
    job_email = job_data['email']
    job_query = job_data["query"]

    if job_query != '':
        filename = f"{job_id}.csv"
        file = open(os.path.join(current_app.config['UPLOAD_DIR'], filename), 'w')
        file.write(job_query)
        file.close()

    db_query = """
    INSERT INTO query (uid, reference, email, date)
    VALUES (?, ?, ?, ?)
    """

    db = db_get()
    cursor = db.cursor()
    cursor.execute(db_query, (job_id, job_reference, job_email, datetime.datetime.now()))
    db.commit()

    current_app.scheduler.submit(job_id)
    current_app.scheduler.poke()

    # todo: send a start/submitted email???
    # if email != "":
    #     send_massage(email, uid, "New", request.base_url)

    return jsonify({'id': job_id})

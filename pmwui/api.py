import datetime
import os
import uuid

from flask import Blueprint, jsonify, request, current_app

from pmwui.db import db_get

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/references", methods=("GET",))
def api_references():
    db = db_get()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM reference")
    ref_name_rows = cursor.fetchall()

    ref_names = [name[0] for name in ref_name_rows]

    return jsonify({"references": ref_names})


@bp.route("/queue_count", methods=("GET",))
def api_queue_count():
    return jsonify({"queue_count": current_app.scheduler.cached_qcount})


@bp.route("/submit", methods=("POST",))
def api_submit():
    job_id = uuid.uuid4()

    print("submit", job_id)

    job_data = request.get_json()

    job_reference = job_data["reference"]
    job_email = job_data["email"]
    job_query = job_data["query"]

    # uid = uuid.uuid4()
    # reference_id = get_reference_from_name(reference)
    filename = ""

    if job_query != "":
        filename = f"{job_id}.csv"
        file = open(os.path.join(current_app.config["UPLOAD_DIR"], filename), "w")
        file.write(job_query)
        file.close()

    db_query = """
    INSERT INTO query (uid, reference, email, date)
    VALUES (?, ?, ?, ?)
    """

    db = db_get()
    cursor = db.cursor()
    cursor.execute(
        db_query, (job_id, job_reference, job_email, datetime.datetime.now())
    )
    db.commit()

    print(current_app.scheduler)

    current_app.scheduler.submit(job_id)
    current_app.scheduler.poke()

    # log.info("########################################")
    # if email != "":
    #     send_massage(email, uid, "New", request.base_url)
    # log.info("result: =S")

    ##############################################################################

    # return jsonify({"id": uid, "url": f"http://127.0.0.1:5000/snp_file/{uid}", "path": f"/snp_files/{uid}"})

    return jsonify({"id": job_id})

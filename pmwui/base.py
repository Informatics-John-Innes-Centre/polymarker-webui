import datetime
import os.path
import uuid
from importlib.metadata import version
import markdown
from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    current_app,
    request,
    flash,
    abort,
)
from werkzeug.utils import redirect
from pmwui.db import db_get
from contextlib import suppress


bp = Blueprint("base", __name__)


def get_version() -> str:
    return version("pmwui")


def get_references():
    db = db_get()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, display_name, description, example FROM reference")
    references = cursor.fetchall()

    proc_ref = []

    for r in references:
        proc_ref.append(r + (markdown.markdown(r[3]),))

    return proc_ref


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        manual_input = request.form["manual_input"]
        query_file = request.files["query_file"]
        reference = request.form["reference"]
        email = request.form["email"]

        if query_file.filename == "" and manual_input == "":
            flash("No input provided.")
            return render_template(
                "base/index.jinja",
                references=get_references(),
                qcount=current_app.scheduler.qcount(),
                version=get_version(),
            )

        job_id = uuid.uuid4()

        if query_file.filename != "":
            query_file.save(
                os.path.join(current_app.config["UPLOAD_DIR"], f"{job_id}.csv")
            )
        else:
            file = open(
                os.path.join(current_app.config["UPLOAD_DIR"], f"{job_id}.csv"), "w"
            )
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

    return render_template(
        "base/index.jinja",
        references=get_references(),
        qcount=current_app.scheduler.qcount(),
        version=get_version(),
    )


# may not need this
@bp.route("/uploads/<job_id>")
def download_file(job_id):
    return send_from_directory(current_app.config["UPLOAD_DIR"], job_id + ".csv")


@bp.route("/results/<job_id>/<filename>")
def result_file(job_id, filename):
    return send_from_directory(
        os.path.join(current_app.config["RESULTS_DIR"], job_id) + "_out", filename
    )


@bp.route("/cite")
def cite():
    return render_template("base/cite.jinja", version=get_version())


@bp.route("/designed_primers")
def designed_primers():
    return render_template("base/designed_primers.jinja", version=get_version())


@bp.route("/about")
def about():
    return render_template(
        "base/about.jinja", references=get_references(), version=get_version()
    )


@bp.route("/results/<job_id>")
def result(job_id):
    db = db_get()
    cursor = db.cursor()
    cursor.execute("SELECT reference, email FROM query WHERE uid = %s", (job_id,))
    reference = cursor.fetchone()

    if reference is None:
        abort(404)

    status = "init"
    with suppress(FileNotFoundError):
        with open(
            f"{current_app.config['RESULTS_DIR']}/{job_id}_out/status.txt", "r"
        ) as f:
            lines = f.read().splitlines()
            status = lines[-1]

    return render_template(
        "base/results.jinja",
        job_id=job_id,
        status=status,
        qcount=current_app.scheduler.qcount(),
        version=get_version(),
    )

import logging
from time import sleep

from flask import url_for
from flask_mail import Message

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)

def send_massage(app_mail, to, job_id, status):
    msg = Message(subject=f'polymarker {job_id} {status}', sender='polymarker@nbi.ac.uk',
                  recipients=[to])
    msg.body = f"""The current status of your request ({job_id}) is {status}
The latest status and results (when done) are available in: {url_for('base.index')}results/{job_id}"""

    log.debug(f"sending mail for job {job_id}")
    app_mail.send(msg)

    # Need to limit the rate at which we send mails or the server will be
    # unhappy with us :(
    sleep(10)

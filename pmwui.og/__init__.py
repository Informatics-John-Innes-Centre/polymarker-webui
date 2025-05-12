
import importlib.metadata



import logging

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)

pmwui_version = importlib.metadata.version('pmwui')




def update_query_status(uid, status):
    dbc = db.connect()
    cursor = dbc.cursor()
    cursor.execute("UPDATE query SET status=? WHERE uid=?", (status, uid))
    dbc.commit()
    cursor.close()
    dbc.close()


def remove_email(uid):
    connection = db.connect()
    cursor = connection.cursor()

    cursor.execute('UPDATE query SET email=NULL WHERE uid=?', (uid,))
    connection.commit()
    connection.close()


def get_reference_from_name(name):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM reference WHERE name = %s", (name,))
    reference = cursor.fetchone()
    connection.close()
    return reference


def get_reference_cmd_data(ref_id):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT path, genome_count, arm_selection FROM reference WHERE id = %s", (ref_id,))
    reference = cursor.fetchone()
    connection.close()
    return reference


def get_query_cmd_data(uid):
    connection = db.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT reference, email FROM query WHERE uid = %s", (uid,))
    reference = cursor.fetchone()
    connection.close()
    return reference

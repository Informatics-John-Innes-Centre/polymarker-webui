import logging
import threading

import mariadb

log = logging.getLogger('gunicorn.error')
logging.basicConfig(level=logging.INFO)


class Scheduler:
    workers = []
    running = False
    event = threading.Event()
    sem = threading.Semaphore()
    work = None
    app = None

    def __init__(self, db_config, app, work):
        self.app = app
        self.work = work
        self.workers.append(threading.Thread(target=self.worker))

    def db_get(self):
        db = mariadb.connect(
            host=self.app.config['DATABASE_HOST'],
            user=self.app.config['DATABASE_USER'],
            password=self.app.config['DATABASE_PASSWORD'],
            database=self.app.config['DATABASE_NAME'],
        )

        return db

    def worker(self):
        while self.running:
            log.debug("scheduler running")
            job = self.get()
            if job is not None:
                log.info(f"executing job: {job[1]}")
                try:
                    db = self.db_get()
                    self.work(db, self.app.config['UPLOAD_DIR'], self.app.config['RESULTS_DIR'], job[1], self.app)
                except Exception as exception:
                    log.error(f"exception raised by worker: {exception}")
                    # todo: do something more than just logging here
                    # update_query_status(work[1], "E: " + str(exception))
                self.delete(job[0])
            else:
                log.info("scheduler queue empty waiting for work...")
                self.event.wait()

    def poke(self):
        log.debug("poking scheduler")
        self.event.set()
        self.event.clear()

    def start(self):
        log.info("starting scheduler")
        self.running = True
        self.workers[0].start()
        self.poke()

    def stop(self):
        log.info("stopping scheduler")
        self.running = False
        self.poke()
        self.workers[0].join()

    def get(self):
        log.debug("fetching next job in the queue")
        self.sem.acquire(blocking=True)
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM cmd_queue WHERE status=?", ("SUB",))
        result = cursor.fetchone()
        if result is not None:
            cursor.execute("UPDATE cmd_queue SET status=? WHERE id=?", ("GOT", result[0]))
            db.commit()
        cursor.close()
        db.close()
        self.sem.release()
        return result

    def submit(self, cmd):
        log.info("submitting job: %s", cmd)
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("INSERT INTO cmd_queue(cmd, status) VALUES (?, ?)", (cmd, "SUB"))
        db.commit()
        cursor.close()
        db.close()

    def delete(self, cmd):
        log.debug("removing job: %s", cmd)
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cmd_queue WHERE id=?", (cmd,))
        db.commit()
        cursor.close()
        db.close()

    def update(self, cmd, status):
        log.debug("updating job: %s with status: %s", cmd, status)
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("UPDATE cmd_queue SET status=? WHERE id=?", (status, cmd))
        db.commit()
        cursor.close()
        db.close()

    def get_queue_len(self):
        log.debug("getting current queue length")
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM cmd_queue")
        queue_len = cursor.fetchone()[0]
        cursor.close()
        db.close()
        log.debug("queue length: %s", queue_len)
        return queue_len

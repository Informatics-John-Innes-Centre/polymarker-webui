import threading
import logging
import mariadb

logger = logging.getLogger(__name__)


class Scheduler:
    workers: list[threading.Thread] = []
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
            host=self.app.config["DATABASE_HOST"],
            user=self.app.config["DATABASE_USER"],
            password=self.app.config["DATABASE_PASSWORD"],
            database=self.app.config["DATABASE_NAME"],
        )

        return db

    def worker(self):
        while self.running:
            logger.info("Scheduler is running")
            job = self.get()
            if job is not None:
                try:
                    db = self.db_get()
                    self.work(
                        db,
                        self.app.config["UPLOAD_DIR"],
                        self.app.config["RESULTS_DIR"],
                        job[1],
                        self.app,
                    )
                except Exception:
                    logger.exception(f"An error occured while executing job: {job}.")
                self.delete(job[0])
            else:
                logger.info("Scheduling is waiting for work")
                self.event.wait()

    def poke(self):
        self.event.set()
        self.event.clear()

    def start(self):
        logger.info("Starting scheduler")
        self.running = True
        self.workers[0].start()
        self.poke()

    def stop(self):
        logger.info("Stopping scheduler")
        self.running = False
        self.poke()
        self.workers[0].join()

    def get(self):
        self.sem.acquire(blocking=True)
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM cmd_queue WHERE status=?", ("SUB",))
        result = cursor.fetchone()
        if result is not None:
            cursor.execute(
                "UPDATE cmd_queue SET status=? WHERE id=?", ("GOT", result[0])
            )
            db.commit()
        cursor.close()
        db.close()
        self.sem.release()
        return result

    def submit(self, cmd):
        logger.info(f"Submitting job {cmd}")
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("INSERT INTO cmd_queue(cmd, status) VALUES (?, ?)", (cmd, "SUB"))
        db.commit()
        cursor.close()
        db.close()

    def delete(self, cmd):
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cmd_queue WHERE id=?", (cmd,))
        db.commit()
        cursor.close()
        db.close()

    def update(self, cmd, status):
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("UPDATE cmd_queue SET status=? WHERE id=?", (status, cmd))
        db.commit()
        cursor.close()
        db.close()

    def qcount(self):
        db = self.db_get()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM cmd_queue")
        qcount = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return qcount

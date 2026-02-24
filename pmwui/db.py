import datetime
import os
import pathlib
import shutil
import subprocess

import mariadb

import click
from flask import current_app, g

import sys

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def db_get():
    if "db" not in g:
        g.db = mariadb.connect(
            host=current_app.config["DATABASE_HOST"],
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            database=current_app.config["DATABASE_NAME"],
        )

    return g.db


def db_close(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def db_init():
    db_cursor = db_get().cursor()

    with current_app.open_resource("schema.sql") as f:
        schema = f.read().decode("utf-8").splitlines()
        for s in schema:
            db_cursor.execute(s)


def generate_indexes(genome_path):
    result = subprocess.run(f"samtools faidx {genome_path}", shell=True)
    if result.returncode > 0:
        #     # if result.returncode == 127:
        #     #     log.info("samtools not found")
        #     # elif result.returncode == 1:
        #     #     log.info(f"failed to open file {path}")
        exit(result.returncode)

    result = subprocess.run(
        f"makeblastdb -dbtype 'nucl' -in {genome_path} -out {genome_path}", shell=True
    )
    # result = subprocess.run(command, shell=True)
    if result.returncode > 0:
        exit(-1)


def db_import(filename):
    with open(filename, "rb") as f:
        genome_desc = tomllib.load(f)

        generate_indexes(genome_desc["path"])

        db_connection = db_get()
        db_cursor = db_connection.cursor()
        db_cursor.execute(
            "INSERT INTO reference (name, display_name, path, genome_count, arm_selection, description, example) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                genome_desc["name"],
                genome_desc["display_name"],
                genome_desc["path"],
                genome_desc["genome_count"],
                genome_desc["arm_selection"],
                genome_desc["description"],
                genome_desc["example"],
            ),
        )
        db_connection.commit()


def db_gc(days):
    time_limit = datetime.datetime.now() - datetime.timedelta(days=days)

    db_connection = db_get()
    db_cursor = db_connection.cursor()
    db_cursor.execute("SELECT id, uid, date FROM query")
    # db_connection.commit()

    entries = db_cursor.fetchall()

    for entry in entries:
        # log.info(entry)
        # log.info(one_hour_ago)
        # log.info(datetime.datetime.fromisoformat(entry[2]))
        if datetime.datetime.fromisoformat(entry[2]) < time_limit:
            db_cursor.execute("DELETE FROM query WHERE id = ?", (entry[0],))
            # log.info("DELETE FROM query WHERE id = ?", (entry[0],))
            try:
                shutil.rmtree(
                    os.path.join(current_app.config["RESULTS_DIR"], f"{entry[1]}_out")
                )
                # shutil.rmtree(os.path.join(current_app.config['UPLOAD_DIR'], f"{entry[1]}.csv"))
                pathlib.Path(
                    os.path.join(current_app.config["UPLOAD_DIR"], f"{entry[1]}.csv")
                ).unlink()
                # log.info(f"{app.static_folder}/data/{entry[1]}_out")
            except FileNotFoundError:
                pass
                # log.info("file not found assume it was never created")
            # log.info(f"{cursor.rowcount} rows were deleted.")
            db_connection.commit()


@click.command("init")
def init_command():
    db_init()
    click.echo("Initialized the database.")


@click.command("import")
@click.argument("filename")
def import_command(filename):
    db_import(filename)
    click.echo("Imported genome.")


@click.command("gc")
@click.argument("days", type=int)
def gc_command(days):
    db_gc(days)
    click.echo("Ran gc.")


def init_app(app):
    app.teardown_appcontext(db_close)
    app.cli.add_command(init_command)
    app.cli.add_command(import_command)
    app.cli.add_command(gc_command)

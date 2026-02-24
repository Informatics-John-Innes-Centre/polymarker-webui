import mariadb

import pytest
from pmwui.db import db_get


def test_get_close_db(app):
    with app.app_context():
        db = db_get()
        assert db is db_get()

    with pytest.raises(mariadb.ProgrammingError) as e:
        db.cursor().execute("SELECT 1")

    assert "Invalid" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("pmwui.db.db_init", fake_init_db)
    result = runner.invoke(args=["init"])
    assert "Initialized" in result.output
    assert Recorder.called


# def test_import_reference_command(runner, monkeypatch):
#     class Recorder(object):
#         called = False
#
#     def fake_init_db(gnfg):
#         Recorder.called = True
#
#     monkeypatch.setattr('pmwui.db.import_reference', fake_init_db)
#
#
#     result = runner.invoke(args=['import-reference', 'tests/160802_Svevo_v2_pseudomolecules.yaml'])
#
#
#     assert "Imported" in result.output


# def test_import_reference(app):
#
#     with app.app_context():
#         import_reference('tests/160802_Svevo_v2_pseudomolecules.yaml')
#         assert get_db().execute(
#             "SELECT * FROM reference WHERE name = 'Durum wheat genome (cv. Svevo)'",
#         ).fetchone() is not None
#
# def test_user_is_created(runner):
#     result = runner.invoke(
#         createsuperuser,
#         input='johnytheuser\nemail@email.com\nsecretpass\nsecretpass'
#     )
#     assert result.exit_code == 0
#     assert ' ' in result.output
#     # etc.

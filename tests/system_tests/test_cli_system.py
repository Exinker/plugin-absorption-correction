import logging
import runpy
import sys


class FakePlugin:

    def run(self, config_xml: str) -> str:
        return '<columns><column id="1" nickname="Ag 338.289" /></columns>'


def test_run_py_prints_process_xml_result(
    capsys,
    monkeypatch,
):
    import plugin

    monkeypatch.setattr(
        plugin.Plugin,
        'create',
        classmethod(lambda cls, correction_preview: FakePlugin()),
    )
    monkeypatch.setattr(
        sys,
        'argv',
        [
            'run.py',
            '--config',
            '<input>C:\\Atom\\Temp\\py_table.xml</input>',
        ],
    )

    try:
        runpy.run_path('run.py', run_name='__main__')

    finally:
        for logger_name in ('plugin-absorption-correction', 'spectrumlab'):
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers:
                handler.close()
            logger.handlers.clear()
            logger.addHandler(logging.NullHandler())

    captured = capsys.readouterr()
    assert captured.out.strip() == '<columns><column id="1" nickname="Ag 338.289" /></columns>'

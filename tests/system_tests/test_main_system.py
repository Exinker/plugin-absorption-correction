import os
from pathlib import Path
from types import SimpleNamespace

import main


def test_main_process_xml_runs_plugin_in_venv_subprocess(monkeypatch):
    calls = []
    config_xml = '<input>C:\\Atom\\Temp\\py_table.xml</input>'

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(stdout='  <columns />\n')

    monkeypatch.setattr(main.subprocess, 'CREATE_NO_WINDOW', 0, raising=False)
    monkeypatch.setattr(main.subprocess, 'run', fake_run)

    result = main.process_xml(config_xml)

    assert result == '<columns />'
    assert len(calls) == 1

    args, kwargs = calls[0]
    assert args == ([
        main.ROOT / '.venv' / 'Scripts' / 'python.exe',
        'run.py',
        '--config',
        config_xml,
    ],)
    assert kwargs['capture_output'] is True
    assert kwargs['creationflags'] == 0
    assert kwargs['text'] is True
    assert kwargs['check'] is True
    assert kwargs['cwd'] == main.ROOT
    pythonpath = kwargs['env']['PYTHONPATH'].split(os.pathsep)
    assert Path(pythonpath[0]) == main.ROOT / '.venv' / 'Lib' / 'site-packages'

import sys
from seed import main
from _pytest.monkeypatch import MonkeyPatch

seed_path = "../seed.py"

def test_params(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', [seed_path])
    main()


test_params(MonkeyPatch() , )
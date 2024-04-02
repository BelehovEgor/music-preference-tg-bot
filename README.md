music-preference-tg-bot
=======================

Dependencies
------------

- [pyenv][pyenv]
- [Poetry][Poetry]

Setup
-----

```sh
pyenv local 3.11
poetry env use $(pyenv which python)
poetry shell
poetry install
```

Run
---

```sh
python3 -m mp-bot
```

[pyenv]:    https://github.com/pyenv/pyenv
[Poetry]:   https://python-poetry.org/

music-preference-tg-bot
=======================

Dependencies
------------

- [pyenv][pyenv]
- [Poetry][Poetry]
- [Docker][Docker]

Setup
-----

### Local ###

```sh
pyenv local 3.11
poetry env use $(pyenv which python)
poetry shell
poetry install
```

### Docker ###

Build image:

```sh
docker build \
    --build-arg TOKEN=${TOKEN} \
    --tag mp-bot .
```

where `${TOKEN}` -- Telegram Bot API token.

Run
---

### Local ###

Add Telegram Bot API token into the code:

```sh
echo 'TOKEN: str = "${TOKEN}"' > mp-bot/configuration.py
```

Run the bot:

```sh
python3 -m mp-bot
```

### Docker ###

Run container:

```sh
docker run \
    --detach \
    --rm \
    --name mp-bot-container \
    mp-bot
```

[pyenv]:    https://github.com/pyenv/pyenv
[Poetry]:   https://python-poetry.org/
[Docker]:   https://www.docker.com/get-started/

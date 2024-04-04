music-preference-tg-bot
=======================

> A bot for sharing tracks with your friends and playlists from different streaming services, like Apple Music, Spotify, etc.

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

Build the image:

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

Run the container:

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

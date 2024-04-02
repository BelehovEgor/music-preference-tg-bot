FROM python:3.11-slim-buster

WORKDIR /bot

COPY . ./

# Install Poetry
RUN pip install poetry
RUN poetry install

# Add Telegram API bot token
ARG TOKEN
ENV TOKEN=${TOKEN}
RUN echo TOKEN: str = \"${TOKEN}\" > mp-bot/configuration.py

CMD ["poetry", "run", "python", "-m", "mp-bot"]

FROM python:3.10-slim-bullseye

RUN mkdir /opt/app
RUN useradd --create-home app
ENV PATH "/home/app/.local/bin:${PATH}"

WORKDIR /opt/app

RUN chown -R app:app /opt/app

USER app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install --user -r requirements.txt

COPY scheduler scheduler

EXPOSE 8000

CMD [ "uvicorn", "scheduler.asgi:app", "--host", "0.0.0.0", "--port", "8000" ]

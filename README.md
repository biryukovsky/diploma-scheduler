## Development

### Run locally
```console
$ uvicorn scheduler.asgi:app --reload
```

### With docker-compose
```console
$ cp .env.example .env
$ docker-compose up --build
```

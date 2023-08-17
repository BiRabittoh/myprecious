# myprecious

## Configuration
```
cp .env.example .env
nano .env
```

### Docker
```
docker-compose up -d
```

### Debug
```
poetry install
poetry run flask --app myprecious run --port 1111 --debug
```


## Production
```
poetry install --with prod
poetry run waitress-serve --port 1111 myprecious:app
```


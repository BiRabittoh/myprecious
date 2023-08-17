# myprecious

## Configuration
```
poetry install --with prod
```

## Usage
```
poetry run waitress-serve --port 1111 myprecious:app
```

### Debug
```
poetry run flask --app myprecious run --port 1111 --debug
```

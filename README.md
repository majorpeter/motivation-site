# Motivation Site

A mini site that shows info to keep you motivated for working out and other stuff.

## Deployment with Docker

* Build and tag container:
```
docker build -t motivation .
```

* Run on default HTTP port (`80`) and clean-up (`--rm`) after closing:
```
docker run --rm -d -p 80:5000 --name motivation motivation
```

## Localization
To extract all messages (generate `*.pot`):
```
pybabel extract -F babel.cfg -o messages.pot .
```
To initialize new translation (e.g. `LANGUAGE_CODE` is `de` for German):
```
pybabel init -i messages.pot -d translations -l <LANGUAGE_CODE>
```
To update messages (*.po files) from template:
```
pybabel update -i messages.pot -d translations
```
To generate binary files (*.mo):
```
pybabel compile -d translations
```

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

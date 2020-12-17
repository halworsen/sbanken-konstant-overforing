# Kæsjflow
Kæsjflow is a small python script that uses the Sbanken API to keep the available balance in one account above a certain threshold by transfering from another.

### Usage
Configure the script by setting up environment variables for the docker container that will be running the script. The simplest way to do this is to make a `.env` file and fill out the required environment variables as described in `.env.example`.

Build the docker image:
```
docker build -t kasjflow .
```
The docker image can then be run with:
```
docker run --env-file .env kasjflow
```

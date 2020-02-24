# Guide for developers
If you're interested in helping to develop Lawliet, please read this file first.

## Preparing a development environment
Before you can start developing Lawliet, you should set up a development environment for it:

- Create a Python virtual environment with all of the dependencies that you need.
- Add a git hook to format your code (optional but requested if you want to commit code to this repository).
- Create a `.env` and/or a `secrets.yml` file defining configuration options.

### Creating a virtual environment
In this repository's root directory, create a new virtual environment with the project dependencies using

```
python3 -m venv venv \
  && source venv/bin/activate \
  && pip install -r requirements.txt \
  && pip install -r requirements.dev.txt
```

If you want to run the functional tests you should also have [geckodriver](https://github.com/mozilla/geckodriver) installed. Download the [latest release of geckodriver](https://github.com/mozilla/geckodriver/releases) from its repository, and make sure that the `geckodriver` executable is somewhere on your system path.

### Code formatting
If you're planning on committing code to this repository, we ask that you use [Black](https://github.com/psf/black) to format your code, so that we have consistent code formatting across the project. We recommend using the script defined in [this gist](https://gist.github.com/kernelmethod/f324f9251faa29b7f042e40f710ab436) as a pre-commit hook; it will check that all of your Python files have correct syntax and that they are formatted appropriately before your code is committed. You can add this hook by running the following from the root directory of this repository:

```
mkdir .git/hooks
wget \
  "https://gist.githubusercontent.com/kernelmethod/f324f9251faa29b7f042e40f710ab436/raw/d58b6082ebc90d5e158656f70cea05dd000b5930/pre-commit" \
  -O .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Creating a `.env` and/or `secrets.yml` file
Lawliet uses environmental variables defined in [`env.dist`](https://github.com/CU-Cybersecurity-Club/lawliet/blob/master/env.dist) and [`deploy_tools/k8s/secrets.yml.dist`](https://github.com/CU-Cybersecurity-Club/lawliet/blob/master/deploy_tools/k8s/secrets.yml.dist) for both testing and deployment. This files serve, respectively, as templates for `.env` and `deploy_tools/k8s/secrets.yml`. In order to test Lawliet locally or deploy it using Kubernetes, you must create one of these two files and provide definitions for all of the environmental variables defined within it.

- `.env` (template: `env.dist`) is used for testing locally with `python3 manage.py` and `docker-compose`.
- `deploy_tools/k8s/secrets.yml` (template: `deploy_tools/k8s/secrets.yml.dist`) is used for testing and deployment with Kubernetes.

## Running tests
This repository provides some basic unit tests and functional tests for development. To run these tests, follow the instructions for creating a development environment and create a `.env` file. Then run the following:

```
source ./venv/bin/activate
cd ./lawliet
python3 manage.py test
```

If you have any problems running the tests, please make sure that you went through all of the steps to create a development environment (including installing geckodriver) before submitting an issue.

## Running the project
We provide three different methods for running this project:

1. Run locally with `manage.py`
2. Run locally with `docker-compose`
3. Run locally / deploy to the cloud with Kubernetes

The first two options are offered primarily for development purposes. The third option can be used either to test locally (with [minikube](https://github.com/kubernetes/minikube)) or to deploy project in its entirety.

### Run locally with `manage.py`
Create a `.env` file from `env.dist`, and then execute

```
source ./venv/bin/activate
cd ./lawliet
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
python3 manage.py runserver
```

This will create a new database, and then run a Django server on http://localhost:8000. You can also use `manage.py` to perform other actions, such as starting a session with your SQL database; run `python3 manage.py --help` to view all of the available options.

Note that if you're just testing locally, you'll probably want to set `DATABASE_ENGINE=sqlite3` in your `.env` file.

### Run with `docker-compose`
If you want to use [docker-compose](https://docs.docker.com/compose/) to test the project, create a `.env` file from `env.dist` and run

```
docker-compose up --build
```

from the repository's root directory. This project uses the [official MariaDB Docker image](https://hub.docker.com/_/mariadb/) for database support; you should review the environmental variables they mention as you create your `.env` file.

### Run with Kubernetes
In order to run the project using Kubernetes, you should first create a `secrets.yml` file with the environmental variables that you would like to use. Create a new [Kubernetes secret](https://kubernetes.io/docs/concepts/configuration/secret/) using

```
kubectl apply -f secrets.yml
```

Then run

```
kubectl apply -f deploy_tools/k8s/dashboard.yml
```

to pull and deploy the container images required to run the project. If you want to test running the project with Kubernetes locally, we suggest using [minikube](https://github.com/kubernetes/minikube) to run a local Kubernetes cluster.

**Note**: If you're developing the project and want to deploy some custom images to your Kubernetes cluster, you should change `deploy_tools/k8s/dashboard.yml` to use those images instead of the defaults.

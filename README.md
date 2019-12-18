## Testing and deployment
In order to run `lawliet-dashboard`, you must either create a `.env` file or a `secrets.yml` file to store environmental variables.

- `.env`: You need a `.env` file if you're going to test the project locally with `lawliet/manage.py` or `docker-compose`. Create one by modifying `env.dist` with the options that you want to use and renaming it to `.env`.
- `secrets.yml`: You'll need a `secrets.yml` file if you're going to deploy `lawliet-dashboard` with Kubernetes. The file `deploy_tools/k8s/secrets.yml.dist` has a template for what the `secrets.yml` file should look like.

### Options for running `lawliet-dashboard`
#### Run locally with `manage.py`
Create a `.env` file in the repository's root directory or in `lawliet/`. Create a virtual environment with the project dependencies using

```
python3 -m venv venv \
  && source venv/bin/activate \
  && pip install -r requirements.txt
```

If you're testing locally, then you'll probably want to use a SQLite database, in which case you'll want to set `DATABASE_ENGINE=sqlite3` in your `.env` file or run `export DATABASE_ENGINE=sqlite3`. Then you can `cd` into the `lawliet/` directory and run `manage.py` to create the database, run the webserver, and more.

#### Run with `docker-compose`
If you want to use [docker-compose](https://docs.docker.com/compose/) to test the project, create a `.env` file from `env.dist` and run

```
docker-compose up --build
```

#### Run with Kubernetes
In order to run the project using Kubernetes, you should first create a `secrets.yml` file with the environmental variables that you would like to use. Create a new [Kubernetes secret](https://kubernetes.io/docs/concepts/configuration/secret/) using

```
kubectl apply -f secrets.yml
```

Then run

```
kubectl apply -f deploy_tools/k8s/dashboard.yml
```

to pull and deploy the container images required to run the project. If you want to test running the project with Kubernetes locally, we suggest using [minikube](https://github.com/kubernetes/minikube) to run a local Kubernetes cluster.

### Unit testing
This repository comes with unit tests for `lawliet-dashboard` to run during development. To run the unit tests, follow the steps in the ["run locally with `manage.py`"](https://github.com/CU-Cybersecurity-Club/lawliet-dashboard#run-locally-with-managepy) section, and then run

```
source venv/bin/activate
cd lawliet
./manage.py test
```

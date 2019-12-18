Authentication portal for pentesting lab environments.

# Usage with Kubernetes
In order to run the webserver with Kubernetes, you must first create a Kubernetes secret with

```
$ kubectl apply -f secrets.yml
```

Then, run

```
$ kubectl apply -f deploy_tools/k8s/dashboard.yml
```

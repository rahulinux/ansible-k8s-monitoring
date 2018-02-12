# Kubernetes Monitoring using Prometheus Operators



# Introduction

This playbook will help you to deploy and setup Prometheus Operators in Kubernetes cluster, this has been tested with RBAC. 

This playbook has two parts:

- Deploy and Configure Prometheus Operators 
- Template for adding services into prometheus 



Let's get start with setup...



# Git repo

You can install directly from the source on gitlab by following these steps:

Clone the repository:

```shell
git clone https://github.com/ansible-k8s-monitoring
cd ansible-k8s-monitoring
```



# Configuration and Usage

This project assumes you have a basic knowledge of how [ansible](https://en.wikipedia.org/wiki/Ansible_(software)) works and have already prepared your hosts for configuration by ansible.

playbook uses `ansible-kubernetes-module`  to deploy on your kubernets cluster, you will need to require `~/.kube/config` which will connect to your kubernetes cluster. You can use `ansible-bootstrap-node` role to configure this.

also this playbook uses to fetch secrets from Vault. so you need to store secrets called `'admin_pass'`, in vault and provide the path inside variable



# Deploy and Configure Prometheus Operators 

**Configure secrets** :

Playbook will read `admin_pass` from vault for grafana, so you need to pass `vault_path` variable

**Install Prometheus operators using**:

```shell
ansible-playbook -e vault_path=/mypath setup_prometheus.yml
```

This will install everything require to run prometheus operators and provides you grafana dashboards to check cluster status. grafana dashboard can be accessable using http://kubernetes-server:30902

---



# Template for adding services into prometheus 



We have one ansible re-usable role called `prometheus-service`,  which will help us to add services into promethues. 



For testing purpose, we have example app which can demonstrate the process. 

Let's deploy the example-app:

```shell
ansible-playbook examples/example_deployment.yml
```

Now add this app into prometheus `setup_services.yml`, create template as below: 

```yaml
---
- hosts: localhost
  gather_facts: no
  tasks:
     - include_role: 
         name: ansible-kubernetes-modules
       vars:
         install_python_requirements: no

     - include_role: 
         name: prometheus-service
       vars:
         app_name: "example-app"
         port_name: "web"
         port: "8080" 
         metrics_path: "/metrics" 
         namespace: default
         selector: 
            app: "example-app" 
```

Deploy it:

```shell
ansible-playbook setup_services.yml
```

Once ou deploy, you can access graph on service NodePort. 

```shell
kubectl get svc example-app-prom 
```

from time import sleep

from click import command, option, secho, Choice, group
from kubernetes import client


@command()
@option("--metric-name", required=True)
def get_external_metric_value(metric_name):
    api = client.CustomObjectsApi()
    resource = api.list_namespaced_custom_object(group="external.metrics.k8s.io", version="v1beta1", namespace="default", plural=metric_name)
    for item in resource["items"]:
        secho(f"Value: {item['value']} - {item['timestamp']}")

@group()
def bastion():
    """
    Grouper of bastion / jump-host utilities that allow us to access resources tied to kubernetes
    while still respecting VPC permissions.

    """
    pass

@bastion.command()
@option("--namespace", default="default")
@option(
    "--image",
    type=Choice(["google/cloud-sdk", "ubuntu", "postgres"]),
    required=True
)
def launch_cli_pod(namespace, image):
    """
    Launch a simple pod with the google cloud CLI pre-installed in order
    to engage with the cluster in a remote shell.

    If you want to test artifact repository permissions, do one of:
    ```
    gcloud auth list
    gcloud auth configure-docker us-central1-docker.pkg.dev
    docker manifest inspect {package}
    ```

    """
    name = "test-cli-pod"
    body = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name,
        },
        "spec": {
            "containers": [
                {
                    #"image": "google/cloud-sdk:latest",
                    "image": f"{image}:latest",
                    "name": name,
                    "command": ["sleep","infinity"]
                }
            ],
            **(
                {
                    "nodeSelector": {
                        "iam.gke.io/gke-metadata-server-enabled": "true"
                    }
                }
                if image == "google/cloud-sdk"
                else {}
            )
        }
    }

    api = client.CoreV1Api()
    api.create_namespaced_pod(body=body, namespace=namespace)

    try:
        secho(f"Launched pod.\nAccess with: `kubectl exec -it {name} --namespace {namespace} -- /bin/bash`", fg="green")

        # TODO: Add check for current status, pending or running

        while True:
            sleep(1)
    except KeyboardInterrupt:
        secho("Shutting down gracefully...")

        api.delete_namespaced_pod(
            namespace=namespace,
            name=name,
        )


@bastion.command()
@option("--namespace", default="default")
@option("--host", required=True)
@option("--database", required=True)
@option("--username", required=True)
@option("--local-port", required=True)
def access_database(namespace, host, database, username, local_port):
    """
    Proxy to the remote database to debug with local psql.

    We faciliate this by spawning a connection pooler into a remote namespace, which
    we expect has VPC firewall access to connect to the database.

    All CLI parameters should be for the RDS database that you wish to access.

    """
    secho("Enter the database password:")
    password = input(" > ")
    if not password:
        raise ValueError("No password specified.")

    name = "database-proxy-pod"
    config_name = f"{name}-config"

    env = {
        "DB_HOST": host,
        "DB_NAME": database,
        "DB_USER": username,
        "DB_PASSWORD": password,
        "AUTH_TYPE": "scram-sha-256"
    }

    # Create a configmap to store the user config file
    # We need to do this manually because the default userlist.txt file uses
    # md5 password encryption. The latest postgres uses scram-sha which is
    # incompatible.
    config_body = {
        "metadata": {
            "name": config_name,
        },
        "data": {
            "userlist.txt": f'"{username}" "{password}"'
        }
    }

    body = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name,
        },
        "spec": {
            "containers": [
                {
                    "image": f"edoburu/pgbouncer:latest",
                    "name": name,
                    "env": [
                        {
                            "name": key,
                            "value": value,
                        }
                        for key, value in env.items()
                    ],
                    "port": {
                        "container_port": 5432
                    },
                    "volumeMounts": [
                        {
                            "name": "config-volume",
                            "mountPath": "/etc/pgbouncer/userlist.txt",
                            "subPath": "userlist.txt"
                        }
                    ]
                }
            ],
            "volumes": [
                {
                    "name": "config-volume",
                    "configMap": {
                        "name": config_name,
                    }
                }
            ]
        }
    }

    api = client.CoreV1Api()

    api.create_namespaced_config_map(body=config_body, namespace=namespace)
    api.create_namespaced_pod(body=body, namespace=namespace)

    try:
        secho(f"Launched pod.\nAccess with: `kubectl port-forward {name} --namespace {namespace} {local_port}:5432`", fg="green")

        # TODO: Add check for current status, pending or running

        while True:
            sleep(1)
    except KeyboardInterrupt:
        secho("Shutting down gracefully...")

        api.delete_namespaced_config_map(
            namespace=namespace,
            name=config_name,
        )

        api.delete_namespaced_pod(
            namespace=namespace,
            name=name,
        )

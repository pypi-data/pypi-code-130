from base64 import b64decode, b64encode

from click import group, option, secho
from kubernetes import client
from rich.console import Console
from rich.table import Table
from rich.text import Text


@group()
def secrets():
    pass


@secrets.command()
@option("--namespace", required=False)
def list(namespace):
    """
    List all current secret keys.

    :param namespace: Optionally filter by namespace

    """
    api = client.CoreV1Api()
    secrets = [
        item
        for item in api.list_secret_for_all_namespaces().items
        if item.metadata.namespace == namespace or namespace is None
    ]

    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Namespace", style="dim")
    table.add_column("Group")
    table.add_column("Secret")

    colors = ["blue", "green"]

    for group_i, item in enumerate(secrets):
        for key in (item.data or {}).keys():
            secret_text = Text(item.metadata.name)
            secret_text.stylize(colors[group_i % len(colors)])

            key_text = Text(key)
            key_text.stylize(colors[group_i % len(colors)])

            table.add_row(item.metadata.namespace, secret_text, key_text)

    console.print(table)


@secrets.command()
@option("--namespace", default="default")
@option("--group", required=True)
@option("--secret", required=True)
@option("--trim", type=bool, default=True)
def edit(namespace, group, secret, trim):
    """
    Add or edit the given secret value.

    Optionally creates a new group if it doesn't exist

    :param trim: By default will trim newlines and whitespaces from around the secret, which
        is useful in situations where you copy+paste from another source.

    """
    api = client.CoreV1Api()
    existing_group = [
        item
        for item in api.list_namespaced_secret(namespace).items
        if item.metadata.name == group
    ]

    if not existing_group:
        secho(f"Group `{group}` not found in namespace `{namespace}`.", fg="yellow")
        secho("Would you like to create it? (yes or no)")
        if input("  > ") != "yes":
            return

        secho("Creating secret group...")
        existing_group.append(
            api.create_namespaced_secret(
                namespace=namespace,
                body=client.V1Secret(
                    metadata=client.V1ObjectMeta(
                        name=group,
                    )
                )
            )
        )

    existing_group = existing_group[0]

    old_secret_value = [
        b64decode(value).decode()
        for key, value in (existing_group.data or {}).items()
        if key == secret
    ]

    if old_secret_value:
        secho(f"Existing secrets value: `{old_secret_value[0]}`", fg="yellow")
    else:
        secho("No existing secrets value found, creating new entry...")

    secho("New value...")
    new_value = input("  > ")

    if trim:
        new_value = new_value.strip()

    existing_group.data = {
        **(existing_group.data or {}),
        secret: b64encode(new_value.encode()).decode()
    }

    api.patch_namespaced_secret(namespace=namespace, name=group, body=existing_group)
    secho("Secret updated successfully", fg="green")


@secrets.command()
@option("--namespace", default="default")
@option("--group", required=True)
@option("--secret", required=True, multiple=True)
def delete(namespace, group, secret):
    """
    Delete the given secret.

    """
    api = client.CoreV1Api()

    existing_group = [
        item
        for item in api.list_namespaced_secret(namespace).items
        if item.metadata.name == group
    ]

    if not existing_group:
        secho(f"Group `{group}` not found in namespace `{namespace}`.", fg="red")
        return

    existing_group = existing_group[0]

    secret_formatted = ", ".join(secret)
    secho(f"Are you sure you want to delete secrets `{secret_formatted}`?\nType the comma separated secret list to confirm.", fg="yellow")
    if input("  > ").replace(" ", "") != secret_formatted.replace(" ", ""):
        return

    existing_group.data = {
        key: value
        for key, value in (existing_group.data or {}).items()
        if key not in secret
    }

    api.patch_namespaced_secret(namespace=namespace, name=group, body=existing_group)

    # If we are deleting the last secret, delete the full secrets container
    if not existing_group.data:
        api.delete_namespaced_secret(namespace=namespace, name=group)

    secho("Secret updated successfully", fg="green")

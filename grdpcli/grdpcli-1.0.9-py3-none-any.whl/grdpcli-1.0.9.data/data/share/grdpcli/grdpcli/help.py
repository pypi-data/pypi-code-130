# Usage

`grdp [command] [resource]`

Use `grdp` to initialize grdp-cli. It will ask for authentification. After authentification it generates two
config files in home directory. One names projects.json and contains projects list and one is for kubernetes.

`[command]` can be type of: 

Configuration commands:

- `update`      updates current configs
- `projects`    prints active project
- `help`        prints help

Basic Commands:
- `get`           Display one or many resources
- `delete`        Delete resources by file names, stdin, resources and names, or by resources and label selector
- `logs`          Print the logs for a container in a pod
- `cp`            Copy files and directories to and from containers
- `exec`          Execute a command in a container

`[resource]` can be type of kuberneetes resource:

- `pod`
- `service`
- `deployment`
- `ingress`
- `namespace`

## Examples
- `$ grdp` - Configure grdp-cli
- `$ grdp update` - Update grdp-cli configuration
- `$ grdp help` - Get grdp-cli help
- `$ kubectl get pods` - Show pods of current project
- `$ kubeclt get service` - Show services of project
- `$ kubectl get ingress` - Show ingress controller
- `$ kubectl logs <pod name>` - Sho logs of selected pod
- `$ kubectl exec -it <pod name>` bash - Execute a command in a selected pod 





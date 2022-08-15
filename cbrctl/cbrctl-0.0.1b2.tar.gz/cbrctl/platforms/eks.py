
EKS_CONFIG_ACTIONS = {
    "helm upgrade -i prometheus \
prometheus-community/kube-prometheus-stack \
--namespace carbonara-monitoring \
-f https://raw.githubusercontent.com/TryCarbonara/CarbonaraResources/main/server-persistent.yaml \
--create-namespace": 60,

    "helm upgrade -i prometheus-pushgateway prometheus-community/prometheus-pushgateway \
--namespace carbonara-monitoring \
--set serviceMonitor.enabled=true \
--set serviceMonitor.namespace=carbonara-monitoring \
--set persistentVolume.enabled=true \
--create-namespace": 20,

    "kubectl apply -f https://raw.githubusercontent.com/TryCarbonara/CarbonaraResources/main/grafana-dashboard-kubectl.yaml \
--namespace carbonara-monitoring": 5,

    "kubectl apply --overwrite=true --namespace carbonara-monitoring -f {{MANIFEST_FILE}}": 10
}
EKS_DECONFIG_ACTIONS = [
"helm uninstall prometheus --namespace carbonara-monitoring",

"helm uninstall prometheus-pushgateway --namespace carbonara-monitoring",

"kubectl delete -f https://raw.githubusercontent.com/TryCarbonara/CarbonaraResources/main/carbonara-agent-manifest.json \
--namespace carbonara-monitoring"
]

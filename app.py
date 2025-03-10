from os import environ
from kubernetes import client, config
from requests import get
from sys import exit
from time import sleep

try:
  config.load_incluster_config()
except:
  config.load_kube_config()

v1 = client.CoreV1Api()

namespace = environ.get("NAMESPACE", "default")
configmap_name = environ.get("CONFIGMAP_NAME", "configmap")
configmap_key = environ.get("CONFIGMAP_KEY", "publicIp")
ip_url = environ.get("IP_URL", "https://api.ipify.org")
interval = int(environ.get("INTERVAL", "300"))

while True:
  config_ip = v1.read_namespaced_config_map(configmap_name, namespace).data[configmap_key]
  ip_resonse = get(ip_url)

  if ip_resonse.status_code != 200:
    print("{ip_url} returned {ip_resonse.status_code}, bai")
    exit(1)

  if config_ip != ip_resonse.text:
    v1.patch_namespaced_config_map(
      name = configmap_name,
      namespace = namespace,
      body = client.V1ConfigMap(
        api_version="v1",
        kind="ConfigMap",
        metadata=client.V1ObjectMeta(name=configmap_name, namespace=namespace),
        data={configmap_key: ip_resonse.text}
      )
    )

  sleep(interval)

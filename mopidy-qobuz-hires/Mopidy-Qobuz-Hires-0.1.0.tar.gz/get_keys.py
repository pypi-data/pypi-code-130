from qobuz_dl.bundle import Bundle

bundle = Bundle()
app_id = bundle.get_app_id()
secrets = "\n".join(bundle.get_secrets().values())

print(f"App ID: {app_id}")

print("#" * 20)

print(f"Secrets (The first usually works):{secrets}")

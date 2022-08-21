#!/usr/bin/env python3

from twine.commands.upload import upload
from twine.settings import Settings

import subprocess

TOKEN = "pypi-AgENdGVzdC5weXBpLm9yZwIkMjZiOGJkNzUtZjIyOS00MmQ5LWIyNjQtNTkzZDI3ZTQ3MmI0AAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiAgny77V7PzfS34CqGkEFSPRiBExqq5TNLYiYfo2iooHA"


subprocess.run(["python", "-m" "build"])

upload(
    upload_settings=Settings(repository_name="testpypi", username="__token__", password=TOKEN),
    dists=["dist/*"],
)

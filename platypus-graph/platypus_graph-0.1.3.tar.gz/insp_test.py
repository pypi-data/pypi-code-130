#!/usr/bin/env python3

import platypus
import inspect

for cls in [platypus.EditGraph, platypus.VMap]:
    print(cls.__name__)
    try:
        print(f"Signature: {inspect.signature(cls)}")
    except ValueError:
        print("No signature")
    names = [name for name, _ in inspect.getmembers(cls) if not name.startswith("__") ]
    hidden = [name for name, _ in inspect.getmembers(cls) if name.startswith("__") ]
    print(f"Members ({len(hidden)} hidden): {names}")
    print()


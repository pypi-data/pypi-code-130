COLLECTION_COLUMN_TYPES_TO_DART = {
    "list<ascii>": ["List", "String"],
    "list<uuid>": ["List", "String"],
    "tuple<float, float, float>": ["Tuple" "float"],
    "list<int>": ["List", "int"],
}

COLUMN_TYPES_TO_DART = {
    # Primitives
    "uuid": "String",
    "ascii": "String",
    "float": "Float",
    "boolean": "bool",
    "int": "int",
    "blob": "Blob",
    # Collections
    "list<ascii>": "List<String>",
    "list<uuid>": "List<String>",
    "tuple<float, float, float>": "Tuple<Float>",
    "list<int>": "List<int>",
}

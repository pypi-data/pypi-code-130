# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations

# Custom Library

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# SQL statements that have been predefined already
# ----------------------------------------------------------------------------------------------------------------------
TRANSLATION_VALUES = (
    lambda language: f"SELECT `tag`, `{language}` FROM `translation_value`;"
)
TRANSLATION_LABELS = (
    lambda language: f"SELECT `tag`, `{language}` FROM `translation_label`;"
)

# ----------------------------------------------------------------------------------------------------------------------
# EXTRA SQL STATEMENTS
# ----------------------------------------------------------------------------------------------------------------------
TRANSLATION_CREATE_EMPTY_TABLES = {
    "translation_label": """
    CREATE TABLE "translation_label" (
        `tag` VARCHAR(255),
        `english` LONGTEXT,
        PRIMARY KEY (`tag`)
    )
    """,
    "translation_value": """
    CREATE TABLE "translation_value" (
        `tag` VARCHAR(255),
        `english` LONGTEXT,
        PRIMARY KEY (`tag`)
    )
    """
}
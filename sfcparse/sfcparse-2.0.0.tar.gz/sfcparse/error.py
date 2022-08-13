# error - Contains base exceptions

# Base Exception
class SfcparseError(Exception):
    """
    sfcparse base exception
    """
    def __init__(self, msg: str, item: str = '') -> None:
        self.msg = str(msg)
        self.item = str(item)

    def __str__(self) -> str:
        return f'[Error] {self.msg} {self.item}'


# Module Exceptions

# General Error
class GeneralError(SfcparseError): __module__ = 'sfcparse.error'

# Native
class ImportFile(SfcparseError): __module__ = 'sfcparse.error'
class ImportFileRaw(SfcparseError): __module__ = 'sfcparse.error'
class ImportAttrs(SfcparseError): __module__ = 'sfcparse.error'
class AppendFile(SfcparseError): __module__ = 'sfcparse.error'
class ExportFile(SfcparseError): __module__ = 'sfcparse.error'
class CleanFormat(SfcparseError): __module__ = 'sfcparse.error'
class SaveFile(SfcparseError): __module__ = 'sfcparse.error'

# Hash
class CompareFileHash(SfcparseError): __module__ = 'sfcparse.error'
class CreateFileHash(SfcparseError): __module__ = 'sfcparse.error'

# JSON
class JsonImportFile(SfcparseError): __module__ = 'sfcparse.error'
class JsonImportStr(SfcparseError): __module__ = 'sfcparse.error'
class JsonExportFile(SfcparseError): __module__ = 'sfcparse.error'
class JsonExportStr(SfcparseError): __module__ = 'sfcparse.error'

# YAML
class YamlImportFile(SfcparseError): __module__ = 'sfcparse.error'
class YamlImportStr(SfcparseError): __module__ = 'sfcparse.error'
class YamlExportFile(SfcparseError): __module__ = 'sfcparse.error'
class YamlExportStr(SfcparseError): __module__ = 'sfcparse.error'

# INI
class IniImportFile(SfcparseError): __module__ = 'sfcparse.error'
class IniExportFile(SfcparseError): __module__ = 'sfcparse.error'
class IniBuildAuto(SfcparseError): __module__ = 'sfcparse.error'

# XML
class XmlImportFile(SfcparseError): __module__ = 'sfcparse.error'
class XmlImportStr(SfcparseError): __module__ = 'sfcparse.error'
class XmlExportFile(SfcparseError): __module__ = 'sfcparse.error'
class XmlExportStr(SfcparseError): __module__ = 'sfcparse.error'

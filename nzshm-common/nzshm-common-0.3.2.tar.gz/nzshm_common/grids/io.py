import base64
import csv
import io
import zipfile


def latlon_from_base64_zip(b64_data: str) -> list:
    result = []
    byte_data = base64.b64decode(b64_data)
    data = io.BytesIO(byte_data)
    with zipfile.ZipFile(data) as fz:
        plain_bytes = io.BytesIO(fz.read("data"))
        reader = csv.reader(io.StringIO(plain_bytes.getvalue().decode("utf-8", "ignore")))
        for row in reader:
            result.append((float(row[1]), float(row[0])))
    return result

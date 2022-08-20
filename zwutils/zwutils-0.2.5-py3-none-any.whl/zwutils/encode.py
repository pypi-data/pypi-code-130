import chardet
from chardet.universaldetector import UniversalDetector

def detect_file_encode(pth):
    """Guess file content encode by chardet. Encoding string is in lower case.

    :param str pth: file path
    :return: {'encoding': 'utf-8', 'confidence': 0.99}
    :rtype: dict
    """
    detector = UniversalDetector()
    detector.reset()
    for line in open(pth, 'rb'):
        detector.feed(line)
        if detector.done: break
    detector.close()
    r = detector.result
    r['encoding'] = r['encoding'].lower()
    return r

def detect_data_encode(rawdata):
    """Guess rawdata encode by chardet. Encoding string is in lower case.

    :param bytes rawdata: file path
    :return: {'encoding': 'utf-8', 'confidence': 0.99}
    :rtype: dict
    """
    r = chardet.detect(rawdata)
    r['encoding'] = r['encoding'].lower()
    return r
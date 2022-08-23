import json
import os
from datetime import datetime

from PyInquirer import ValidationError, Validator

root_dir = os.path.expanduser(os.path.join('~', '.wavecount_cli'))
filename = os.path.expanduser(root_dir + '/config.json')


def read_config():
    cfg = {}
    if not os.path.exists(filename):
        os.makedirs(root_dir, exist_ok=True)
        with open(filename, 'w+') as cfg_file:
            json.dump(cfg, cfg_file, indent=4)
    else:
        with open(filename, 'r') as cfg_file:
            cfg = json.load(cfg_file)
    return cfg


def save_config(cfg):
    with open(filename, 'w') as cfg_file:
        return json.dump(cfg, cfg_file, indent=4)


class SerialNumberValidate(Validator):
    def validate(self, document):
        if not (isinstance(document.text, str) and len(str(document.text)) >= 10):
            raise ValidationError(
                message='"{}" is not a valid serial-number. should be at least 10 characters'.format(document.text),
                cursor_position=len(document.text))
        else:
            return True


class PartNumberValidate(Validator):
    def validate(self, document):
        if not (isinstance(document.text, str) and len(str(document.text)) >= 4):
            raise ValidationError(
                message='"{}" is not a valid part-number. should be at least 40 characters'.format(document.text),
                cursor_position=len(document.text))
        else:
            return True


class DateValidate(Validator):
    def validate(self, document):
        try:
            datetime.strptime(document.text, '%Y-%m-%d')
            return True
        except ValueError:
            raise ValidationError(
                message='"{}" incorrect date format, should be <YYYY-MM-DD>'.format(document.text),
                cursor_position=len(document.text))


class DatetimeValidate(Validator):
    def validate(self, document):
        try:
            datetime.strptime(document.text, '%Y-%m-%d %H:%M')
            return True
        except ValueError:
            raise ValidationError(
                message='"{}" incorrect datetime format, should be <YYYY-MM-DD HH:mm>'.format(document.text),
                cursor_position=len(document.text))


class StringValidate(Validator):
    def validate(self, document):
        chars_limit = 1
        if not (isinstance(document.text, str) and len(str(document.text)) >= chars_limit):
            raise ValidationError(
                message='"{}" is not a valid. should be at least {} characters'.format(document.text, chars_limit),
                cursor_position=len(document.text))
        else:
            return True


class IntValidate(Validator):
    def validate(self, document):
        digits_limit = 1
        if len(str(document.text)) < 1:
            raise ValidationError(
                message='"{}" is not valid. should be at least {} digits'.format(document.text, digits_limit),
                cursor_position=len(document.text)
            )
        try:
            int(document.text)
            return True
        except ValueError:
            raise ValidationError(
                message='"{}" is not valid. should be digit'.format(document.text),
                cursor_position=len(document.text))

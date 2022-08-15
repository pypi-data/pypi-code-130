from robot.libraries import Collections, String, DateTime, OperatingSystem
import json


class Base(Collections, String, DateTime, OperatingSystem):
    @staticmethod
    def convert_to_json(dict_data):
        if isinstance(dict_data, str):
            try:
                # 如果可以会转为dict或list
                dict_data = json.loads(dict_data)
            except ValueError:
                pass
        if isinstance(dict_data, (dict, list)):
            dict_data = json.dumps(dict_data, sort_keys=True, indent=4, ensure_ascii=False, separators=(',', ':'))
        if isinstance(dict_data, int):  # 字符串数字会因为 json.loads 转为 int 导致request报错
            dict_data = str(dict_data)
        return dict_data

    def json_output(self, dict_data):
        print(self.convert_to_json(dict_data))


    def _base_doc(self):
        pass

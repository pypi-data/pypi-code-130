import pytz
import datetime as dt
import numpy as np
import pandas as pd

import os
import json

class dictionary:
    def __init__(self,input):
        self.object = input

    def get_value_from_path(self,path):
        path_string="["+"][".join(path.split("."))+"]"
        dict_object=self.object
        exec("output=dict_object"+path_string,globals(),locals())
        return output
    def get_elements(self, position, **kwargs):
        keys = list({k for d in self.object for k in d.keys()})
        values = list({k for d in self.object for k in d.values()})
        if position == "k":
            return keys
        elif position == "v":
            return values
        elif position == "b":
            separator = kwargs.get("separator", '')
            return [k + separator + v for k, v in zip(keys, values)]


    def keys_filtering(self, filter_list):
        """User defined function to filter in dictionary over keys and return values"""
        return list([list(item.values())[0] for item in self.object if list(item.keys())[0] in filter_list])

    def formatting(self,formatting_type,**kwargs):
        import re

        if formatting_type== "bq_conversion":
            schema_master = kwargs["schema"]
            if type(self.object) != list and type(schema_master) == list:
                self.object =  [self.object]

        if type(self.object) == list:
            output=[]

            if formatting_type == "types_parsing":
                if type(self.object[0]) == dict:
                    rows_union = {}
                    for idx,row in enumerate(input):
                            row_formatted = dictionary.formatting(row, formatting_type, **kwargs)
                            rows_union=dictionary.merge(rows_union,row_formatted)
                    output = [rows_union]
                else:
                    rows_union=[]
                    for idx,row in enumerate(self.object):
                            row_formatted = dictionary.formatting(row, formatting_type, **kwargs)
                            rows_union= list({s for s in rows_union + [row_formatted]})
                    output = rows_union

            else:
                for idx, row in enumerate(self.object):
                    if formatting_type == "bq_conversion":
                        kwargs["schema"]=kwargs["schema"][0] if type(kwargs["schema"]) == list else kwargs["schema"]
                    row_formatted=dictionary.formatting(row,formatting_type,**kwargs)
                    output.append(row_formatted)

        elif type(self.object) == dict:

            output={}

            for k,v in dict(self.object).items():
                if v in [None,{},'None']:
                    pass

                else:
                    if formatting_type == "bq_conversion":
                        if type(schema_master) == list:
                            if type(input) != list:
                                output = dictionary.formatting([self.object], formatting_type, schema=schema_master[0])
                            else:
                                output = dictionary.formatting(self.object, formatting_type, schema=schema_master[0])
                        else:
                            try:
                                kwargs["schema"] = schema_master[k]
                                output[k] = dictionary.formatting(v, formatting_type, **kwargs)
                                if not re.match(r'^\w+$', k):
                                    k_new = re.sub(r'\W+', '', k)
                                    output[k_new] = output.pop(k)
                            except KeyError as e:
                                if kwargs["pass_unknown_values"]==True:
                                    pass
                    else:
                        output[k] = dictionary.formatting(v, formatting_type, **kwargs)

                        if not re.match(r'^\w+$', k) and formatting_type =="key_normalization" :
                            k_new = re.sub(r'\W+', '', k)
                            output[k_new] = output.pop(k)

        else:
            if formatting_type == "bq_conversion" and schema_master != type(input).__name__:
                output_type = kwargs["schema"]
                output = dictionary.type_converting(self.object,manual_type=output_type)
            elif formatting_type == "types_parsing":
                output = type(self.object).__name__
            elif formatting_type == "custom_conversion":
                    output=kwargs["conversion_dict"][self.object]
            else:
                output = self.object

        return output


    @staticmethod
    def type_converting(value,**kwargs):
        import uuid
        import datetime
        import decimal
        if type(value) in [uuid.UUID,datetime.datetime,datetime.date]:
            value = str(value)
        elif value in [[],{}]:
            value = None
        elif type(value) in [decimal.Decimal]:
            value = float(value)
        elif "manual_type" in kwargs:
            try:

                local_dict={"value":value}
                exec("value = " + kwargs["manual_type"] + "(value)",globals(),local_dict)
                value = local_dict["value"]
            except Exception as e:
                str(e)
        return value

    @staticmethod
    def merge(dict_1,dict_2):
        for key, value in dict_2.items():
            if key in dict_1:
                if isinstance(dict_1[key], dict) and isinstance(dict_2[key], dict):
                    dictionary.merge(dict_1[key],dict_2[key])
                elif isinstance(dict_1[key],dict) and isinstance(dict_2[key],list):
                    dict_1[key]=dict_2[key]
            else:
                dict_1[key] = value
        return dict_1


class lists:
    def __init__(self,list_object):
        self.object=list_object

    def join_string(self,separator=','):
        """Compiler of list of strings of code into string chain (in case of >1 elements) or simple value given by
        returned data type. """
        if len(self.object) == 1:
            return eval(self.object[0])
        else:
            return separator.join([str(eval(i)) for i in self.object])

    def clean_currency(self):
        return self.object.str.replace(",", ".").str.replace("Kč", "").str.replace(" ", "").astype(float)

    def remove_duplicates(self):
        return list(set([i for i in self.object]))

    def get_values_by_key(self,key="name"):
        return list(set([i[key] for i in self.object if key in i.keys()]))
    def get_element_by_name(self,name="",key="name"):
        return [i for i in self.object if name in i[key]][0]


class time:
    @staticmethod
    def iso(date_input):
        tz = pytz.timezone("Europe/Prague")
        output= tz.localize(dt.datetime.combine(date_input, dt.time())).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return output


    @staticmethod
    def today(granularity="datetime"):
        input = dtd.now()
        if granularity=="date":
            output=input.strftime("%Y-%m-%d")
        elif granularity=="datetime":
            output=input.strftime("%Y-%m-%dT%H:%M:%S")
        return output

    @staticmethod
    def today_plus(granularity="datetime",dplus=0,out_format="string"):
        date_add = (dt.datetime.now() + dt.timedelta(days=dplus))
        if out_format == "string":
            output=date_add.strftime("%Y-%m-%dT%H:%M:%S")
            output = output[:10] if granularity == "date" else output
        else:
            output=date_add

        return output


class pandas:
    @staticmethod
    def range_join(config, values):
        a = config["main_table"][values].values
        bh = config["matching_table"]["max"].values
        bl = config["matching_table"]["min"].values

        i, j = np.where((a[:, None] >= bl) & (a[:, None] <= bh))

        return pd.DataFrame(
            np.column_stack([config["main_table"].values[i], config["matching_table"].values[j]]),
            columns=config["main_table"].columns.append(config["matching_table"].columns),
            index=config["main_table"].index
        )


class local:
    @staticmethod
    def read_configJSON(path,output_type="dict"):
        with open("./" + os.environ.get("CONFIG_PATH",'') + path + ".json") as f:
            if output_type == "dict":
                return json.load(f)
            elif output_type == "string":
                return f.read()

    @staticmethod
    def read_keysJSON(path,output_type="dict"):
        with open("./" + os.environ.get("KEYS_PATH",'') + path + ".json") as f:
            if output_type == "dict":
                return json.load(f)
            elif output_type == "string":
                return f.read()


class query:
    @staticmethod
    def get_last_value(column,tablePath):
        query_string = 'SELECT MAX({}) FROM `{}`'.format(column,tablePath)
        return query_string


def timeit(method):
    import time
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            print('%r  %2.2f s' % \
                  (method.__name__, (te - ts)))
        return result
    return timed
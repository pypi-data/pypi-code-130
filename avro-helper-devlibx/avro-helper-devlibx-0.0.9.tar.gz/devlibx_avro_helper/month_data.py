import io
import avro.schema
import avro.io
import base64
from datetime import datetime
from datetime import timedelta

month_data_schema = '''
{
  "namespace": "io.gitbub.devlibx.avro",
  "type": "record",
  "name": "MonthDataAvro",
  "fields": [
    {
      "name": "days",
      "type": [
        "null",
        {
          "type": "map",
          "values": "int"
        }
      ],
      "default": null
    },
    {
      "name": "days_str",
      "type": [
        "null",
        {
          "type": "map",
          "values": "string"
        }
      ],
      "default": null,
      "doc": "map of days data as string"
    },
    {
      "name": "entity_id",
      "type": [
        "null",
        "string"
      ],
      "default": null
    },
    {
      "name": "sub_entity_id",
      "type": [
        "null",
        "string"
      ],
      "default": null
    },
    {
      "name": "version",
      "type": "int",
      "default": 1
    }
  ]
}
'''

month_data_schema_parsed = avro.schema.parse(month_data_schema)


# This class helps to read avro object from given Base64 string
# noinspection PyMethodMayBeStatic
class MonthDataAvroHelper:
    def __int__(self):
        pass

    def process(self, avro_base64_str):
        """
        Process the input Base64 data

        :param avro_base64_str: Base46 coded data
        :return: Deserialize Avro object
        """
        bytes_reader = io.BytesIO(base64.b64decode(avro_base64_str))
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(month_data_schema_parsed)
        return reader.read(decoder)

    def process_and_return_last_n_days_from_time(self, time, avro_base64_str, days):
        """
        Return N days in past (including today) data from the time given in "time"

        :param datetime time: Time from where we need to calculate N days
        :param str avro_base64_str: Base64 data of month data
        :param int days: How many days in past
        :return: Array containing N items (N = days)
        """

        data = self.process(avro_base64_str)
        print(data)
        days_to_add = self.get_last_n_days_keys(time, days)
        result = []
        for day in days_to_add:
            try:
                result.append(data["days"][day])
            except KeyError as error:
                pass
        return result

    def process_and_return_last_n_days(self, avro_base64_str, days):
        """
        Return N days in past (including today) data from today

        :param str avro_base64_str: Base64 data of month data
        :param int days: How many days in past
        :return: Array containing N items (N = days)
        """
        return self.process_and_return_last_n_days_from_time(datetime.now(), avro_base64_str, days)

    def get_last_n_days_keys(self, time, days):
        """
        Give key from given time to N days - you can use these keys to get data from avro data

        :param time: time to start
        :param days: no of days
        :return: array containing keys for past N days (including given time)
        """
        result = []
        end = time
        start = time - timedelta(days=days)
        while start < end:
            start = start + timedelta(days=1)
            result.append("{}-{}".format(start.month, start.day))
        return result

    def get_last_n_days_keys_from_now(self, days):
        """
       Give key from now to N days - you can use these keys to get data from avro data

       :param time: time to start
       :param days: no of days
       :return: array containing keys for past N days (including today)
       """
        time = datetime.now()
        return self.get_last_n_days_keys(time, days)

    def get_keys_for_month(self, time):
        """
        Give key month given by time - you can use these keys to get data from avro data

        :param time: month to use
        :return: array containing keys for this month (including given time)
        """
        result = []
        end = time
        start = time.replace(day=1)
        while start <= end:
            result.append("{}-{}".format(start.month, start.day))
            start = start + timedelta(days=1)
        return result

    def get_keys_for_this_month(self):
        """
        Give key month this month

        :return: array containing keys for this month (including given time)
        """
        return self.get_keys_for_month(datetime.now())

    def get_keys_for_week(self, time):
        """
        Give key month given by time - you can use these keys to get data from avro data

        :param time: month to use
        :return: array containing keys for this month (including given time)
        """
        result = []
        end = time
        start = time - timedelta(days=6)
        while start <= end:
            result.append("{}-{}".format(start.month, start.day))
            start = start + timedelta(days=1)
        return result

    def get_keys_for_this_week(self):
        """
        Give key month this month

        :return: array containing keys for this month (including given time)
        """
        return self.get_keys_for_week(datetime.now())

    def process_and_return_aggregation_for_month(self, time, avro_base64_str, aggregate=True):
        """
        Return data for month given by time (including today)

        :param datetime time: Time from where we need to calculate N days
        :param str avro_base64_str: Base64 data of month data
        :param aggregate if true add and return sum, otherwise array
        :return: Array containing N items (N = days) OR aggregated sum if aggregate=true
        """

        data = self.process(avro_base64_str)
        days_to_add = self.get_keys_for_month(time)
        result = []
        for day in days_to_add:
            try:
                result.append(data["days"][day])
            except KeyError as error:
                pass
        if aggregate is False:
            return result
        else:
            sum = 0
            for i in result:
                sum = sum + i
            return sum

    def process_and_return_aggregation_for_this_month(self, avro_base64_str, aggregate=True):
        """
        Return data for this month (including today)

        :param str avro_base64_str: Base64 data of month data
        :param aggregate if true add and return sum, otherwise array
        :return: Array containing N items (N = days) OR aggregated sum if aggregate=true
        """
        return self.process_and_return_aggregation_for_month(datetime.now(), avro_base64_str, aggregate)

    def process_and_return_aggregation_for_week(self, time, avro_base64_str, aggregate=True):
        """
        Return data for week given by time (including today)

        :param datetime time: Time from where we need to calculate N days
        :param str avro_base64_str: Base64 data of month data
        :param aggregate if true add and return sum, otherwise array
        :return: Array containing N items (N = days) OR aggregated sum if aggregate=true
        """

        data = self.process(avro_base64_str)
        days_to_add = self.get_keys_for_week(time)
        result = []
        for day in days_to_add:
            try:
                result.append(data["days"][day])
            except KeyError as error:
                pass
        if aggregate is False:
            return result
        else:
            sum = 0
            for i in result:
                sum = sum + i
            return sum

    def process_and_return_aggregation_for_this_week(self, avro_base64_str, aggregate=True):
        """
        Return data for this week (including today)

        :param str avro_base64_str: Base64 data of month data
        :param aggregate if true add and return sum, otherwise array
        :return: Array containing N items (N = days) OR aggregated sum if aggregate=true
        """
        return self.process_and_return_aggregation_for_week(datetime.now(), avro_base64_str, aggregate)
